import math, threading, time, uuid
from random import Random
from .grid import WarehouseGrid
from .robot import Robot
from ..ai.anomaly import EdgeAnomalyEngine
from ..storage.db import EventDB

class FleetRuntime:
    def __init__(self):
        self.lock=threading.RLock(); self.rng=Random(11)
        self.grid=WarehouseGrid(); self.ai=EdgeAnomalyEngine(); self.db=EventDB()
        self.robots={}; self.tasks=[]; self.messages=0; self.negotiations=0; self.collisions=0
        self.tick_count=0; self.running=True; self.packet_loss=0.0; self.network_partition=set(); self.event_buffer=[]
        self._make_fleet(5)
        self.thread=threading.Thread(target=self._loop,daemon=True); self.thread.start()

    def log(self, level,event,data=None):
        item={'ts':time.time(),'level':level,'event':event,'data':data or {}}
        self.event_buffer.append(item); self.event_buffer=self.event_buffer[-200:]
        self.db.event(level,event,data)

    def _make_fleet(self,n):
        self.robots={}
        for i in range(n):
            p=(1+i%3,1+i//3)
            self.robots[f'AMR-{i+1}']=Robot(f'AMR-{i+1}',p,rng=Random(100+i))
        self._seed_tasks(max(12,n*2))

    def _seed_tasks(self,n):
        self.tasks=[]
        for i in range(n):
            self.tasks.append({'id':f'T-{i+1}','pickup':(2+(i*3)%14,2+(i*5)%14),'dropoff':(14-(i*2)%12,14-(i*3)%12),'priority':1+(i%10),'status':'queued','assigned_to':None,'created':self.tick_count})

    def reset(self,count=5):
        with self.lock:
            self.grid=WarehouseGrid(); self.messages=self.negotiations=self.collisions=self.tick_count=0; self.packet_loss=0; self.network_partition=set(); self._make_fleet(count)
            self.log('INFO','fleet_reset',{'robots':count})

    def scale(self,count):
        with self.lock:
            old=len(self.robots); self._make_fleet(count); self.log('INFO','fleet_scaled',{'from':old,'to':count})

    def add_task(self,pickup=(1,1),dropoff=(14,14),priority=5):
        with self.lock:
            t={'id':f'T-{uuid.uuid4().hex[:6]}','pickup':pickup,'dropoff':dropoff,'priority':priority,'status':'queued','assigned_to':None,'created':self.tick_count}; self.tasks.append(t); self.log('INFO','task_created',t); return t

    def _assign_tasks(self):
        # Requeue work owned by failed/isolated robots so healthy peers can bid again.
        for t in self.tasks:
            rid=t.get('assigned_to')
            if t.get('status') in ('assigned','transporting') and rid in self.robots:
                owner=self.robots[rid]
                if (not owner.alive) or (not owner.connected):
                    t['status']='queued'; t['assigned_to']=None
                    owner.task_id=None; owner.goal=None; owner.path=[]; owner.load=0.0
                    self.log('WARN','task_requeued_after_fault',{'task':t['id'],'failed_robot':rid})
        for t in sorted([x for x in self.tasks if x['status']=='queued'], key=lambda x:-x['priority']):
            bids=[]
            for r in self.robots.values():
                if not r.alive or not r.connected or r.battery<15 or r.task_id: continue
                d=abs(r.pos[0]-t['pickup'][0])+abs(r.pos[1]-t['pickup'][1])
                bids.append((d+max(0,50-r.battery)*0.08+r.anomaly_risk*8,r))
            if bids:
                _,r=min(bids,key=lambda x:x[0]); r.task_id=t['id']; r.goal=tuple(t['pickup']); r.path=self.grid.astar(r.pos,r.goal); r.state='to_pickup'; t['status']='assigned'; t['assigned_to']=r.robot_id
                self.messages+=max(1,len(self.robots)-1); self.log('INFO','distributed_task_award',{'task':t['id'],'robot':r.robot_id})

    def _neighbors(self,r):
        # Simulated P2P intent/state exchange. Partitioned nodes cannot receive updates.
        for other in self.robots.values():
            if other.robot_id==r.robot_id: continue
            if r.robot_id in self.network_partition or other.robot_id in self.network_partition: continue
            if self.rng.random()>=self.packet_loss: self.messages+=1

    def _propose(self, r):
        if not r.alive: return r.pos
        if not r.connected: return r.pos
        if not r.task_id: return r.pos
        if not r.path or r.path[0] != r.pos:
            r.path=self.grid.astar(r.pos,r.goal) if r.goal else []
        return r.path[1] if len(r.path)>1 else r.pos

    def _finish_move(self, r, nxt):
        if not r.alive or not r.connected:
            r.state='failed' if not r.alive else 'network_isolated'; return
        if nxt != r.pos:
            r.pos=nxt
            if r.path and r.path[0]==r.pos: r.path=r.path[1:]
            r.state='moving'; r.wait_ticks=0; r.tick_energy()
        elif r.task_id:
            r.wait_ticks+=1; r.state='yielding' if r.wait_ticks else 'waiting'
        else:
            r.state='idle'; r.tick_energy()
        if r.goal and r.pos==r.goal:
            t=next((x for x in self.tasks if x['id']==r.task_id),None)
            if t and t['status']=='assigned' and tuple(t['pickup'])==r.goal:
                t['status']='transporting'; r.goal=tuple(t['dropoff']); r.path=self.grid.astar(r.pos,r.goal); r.load=1.0; r.state='carrying'
            elif t and t['status']=='transporting' and tuple(t['dropoff'])==r.goal:
                t['status']='completed'; r.completed+=1; r.task_id=None; r.goal=None; r.path=[]; r.load=0.0; r.state='idle'; self.log('INFO','task_completed',{'task':t['id'],'robot':r.robot_id})

    def tick(self):
        with self.lock:
            self.tick_count+=1
            self._assign_tasks()
            # Heartbeat/intent fan-out over the simulated peer mesh.
            connected=[r for r in self.robots.values() if r.alive and r.connected]
            for r in connected:
                for other in connected:
                    if r.robot_id==other.robot_id: continue
                    if self.rng.random() >= self.packet_loss: self.messages += 1
            proposals={r.robot_id:self._propose(r) for r in self.robots.values()}
            winners={}
            # Same-target reservations: one robot wins, others yield.
            by_target={}
            for rid,nxt in proposals.items():
                if nxt!=self.robots[rid].pos: by_target.setdefault(nxt,[]).append(rid)
            for target,rids in by_target.items():
                winner=min(rids,key=lambda rid:(-int(self.robots[rid].battery>20),rid))
                for rid in rids:
                    if rid!=winner: proposals[rid]=self.robots[rid].pos; self.negotiations+=1
                if len(rids)>1:self.negotiations+=1
            # A robot may enter an occupied cell only when its occupant also moves away.
            old={r.robot_id:r.pos for r in self.robots.values()}
            for rid,nxt in list(proposals.items()):
                if nxt==old[rid]: continue
                occupant=next((oid for oid,p in old.items() if oid!=rid and p==nxt),None)
                if occupant is not None and proposals.get(occupant)==old[occupant]:
                    proposals[rid]=old[rid]; self.negotiations+=1
            # Prevent direct swaps (A→B while B→A) because the discrete simulator has no passing space.
            ids=list(self.robots)
            for i,a in enumerate(ids):
                for b in ids[i+1:]:
                    ra,rb=self.robots[a],self.robots[b]
                    if proposals[a]==rb.pos and proposals[b]==ra.pos and ra.pos!=rb.pos:
                        proposals[a]=ra.pos; proposals[b]=rb.pos; self.negotiations+=1
            # A reservation snapshot makes all accepted moves simultaneous.
            for r in self.robots.values():
                self._finish_move(r,proposals[r.robot_id])
                r.anomaly_risk=self.ai.score(r.battery,r.temperature,r.speed,r.load)
                if r.alive and r.anomaly_risk>.72 and r.state not in ('failed','network_isolated'): r.state='ai_alert'
                if r.battery<8 and r.alive:
                    r.alive=False; r.state='battery_fail'; self.log('WARN','predictive_battery_shutdown',{'robot':r.robot_id})
            # Safety invariant: no two robots may occupy the same cell after a tick.
            positions={}
            for r in self.robots.values():
                if r.alive:
                    if r.pos in positions: self.collisions+=1
                    positions[r.pos]=r.robot_id
            if self.tick_count%50==0: self.log('INFO','fleet_heartbeat',{'tick':self.tick_count,'messages':self.messages})

    def _loop(self):
        while self.running:
            time.sleep(.12)
            try:self.tick()
            except Exception as e:self.log('ERROR','simulation_error',{'error':str(e)})

    def fault_robot(self,rid):
        with self.lock:
            if rid in self.robots: self.robots[rid].alive=False; self.robots[rid].state='failed'; self.log('WARN','robot_failure_injected',{'robot':rid})

    def recover_robot(self,rid):
        with self.lock:
            if rid in self.robots: self.robots[rid].alive=True; self.robots[rid].connected=True; self.robots[rid].battery=max(self.robots[rid].battery,55); self.robots[rid].state='recovered'; self.log('INFO','robot_recovered',{'robot':rid})

    def partition(self,rid,enabled):
        with self.lock:
            if enabled:self.network_partition.add(rid)
            else:self.network_partition.discard(rid)
            if rid in self.robots:self.robots[rid].connected=not enabled
            self.log('WARN' if enabled else 'INFO','network_partition',{'robot':rid,'isolated':enabled})

    def block(self,p):
        with self.lock:
            self.grid.blocked.add(tuple(p)); self.log('WARN','aisle_blocked',{'cell':p})
            for r in self.robots.values():
                if r.goal: r.path=self.grid.astar(r.pos,r.goal)

    def unblock(self,p):
        with self.lock:
            self.grid.blocked.discard(tuple(p)); self.log('INFO','aisle_unblocked',{'cell':p})

    def set_congestion(self,level):
        with self.lock:self.grid.congestion=level; self.log('INFO','congestion_changed',{'level':level})

    def force_conflict(self):
        with self.lock:
            alive=list(self.robots.values())[:2]
            if len(alive)>=2:
                a,b=alive; a.pos=(6,5); b.pos=(6,7); a.goal=(6,7); b.goal=(6,5); a.path=self.grid.astar(a.pos,a.goal); b.path=self.grid.astar(b.pos,b.goal); a.task_id=a.task_id or 'T-CONFLICT-A'; b.task_id=b.task_id or 'T-CONFLICT-B'; self.log('WARN','forced_intersection_conflict',{'robots':[a.robot_id,b.robot_id]})

    def status(self):
        with self.lock:
            robots=[]
            for r in self.robots.values(): robots.append({'id':r.robot_id,'x':r.pos[0],'y':r.pos[1],'alive':r.alive,'connected':r.connected,'state':r.state,'task':r.task_id,'goal':r.goal,'completed':r.completed,'telemetry':r.telemetry(),'path':r.path[:25]})
            return {'tick':self.tick_count,'robots':robots,'tasks':self.tasks[-80:],'metrics':{'collisions':self.collisions,'negotiations':self.negotiations,'p2p_messages':self.messages,'completed_tasks':sum(r.completed for r in self.robots.values()),'fleet_size':len(robots),'active':sum(r.alive for r in self.robots.values()),'partitioned':len(self.network_partition),'blocked_cells':len(self.grid.blocked),'congestion':self.grid.congestion},'grid':{'width':self.grid.width,'height':self.grid.height,'blocked':[list(p) for p in sorted(self.grid.blocked)]},'network':{'packet_loss':self.packet_loss}}

    def benchmark(self):
        # Deterministic planning workload model: distributed execution runs in parallel batches; baseline serializes jobs.
        with self.lock:
            tasks=max(20,len(self.tasks)); fleet=max(3,len(self.robots)); base=tasks*3.2
            distributed=base/max(1,min(fleet,20)) + 4.0 + self.grid.congestion*base*.18
            improvement=max(0,min(95,100*(1-distributed/base)))
            result={'tasks':tasks,'robots':fleet,'distributed_time':round(distributed,2),'stop_and_wait_time':round(base,2),'improvement_percent':round(improvement,1),'collisions':self.collisions,'network_packet_loss':self.packet_loss,'note':'simulation estimate for comparative experiments, not a physical-world guarantee'}
            self.db.experiment('distributed_vs_stop_wait',result); self.log('INFO','benchmark_completed',result); return result

    def run_experiment(self,robot_counts,ticks):
        rows=[]
        with self.lock: original=len(self.robots)
        for n in robot_counts:
            self.reset(n); time.sleep(.02)
            start_completed=sum(r.completed for r in self.robots.values()); start=time.time()
            for _ in range(ticks): self.tick()
            elapsed=time.time()-start; done=sum(r.completed for r in self.robots.values())-start_completed
            rows.append({'robots':n,'ticks':ticks,'completed_tasks':done,'messages':self.messages,'negotiations':self.negotiations,'collisions':self.collisions,'tasks_per_tick':round(done/max(1,ticks),4),'messages_per_tick':round(self.messages/max(1,ticks),2),'elapsed_sim_seconds':round(elapsed,3)})
        self.reset(original); self.db.experiment('scalability',rows); return rows
