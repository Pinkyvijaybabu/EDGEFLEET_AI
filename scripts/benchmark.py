from app.core.fleet import FleetRuntime

if __name__=='__main__':
    f=FleetRuntime()
    print('Comparative benchmark:')
    print(f.benchmark())
    print('\nScalability:')
    for row in f.run_experiment([5,10,25,50,100],50): print(row)
