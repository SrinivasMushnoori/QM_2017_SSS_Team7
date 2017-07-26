"""
this is to solve the converged charge matrix 
"""

import psi4
import numpy as np
def solve(mints,nel,mol):
    
    V=np.array(mints.ao_potential())
    T=np.array(mints.ao_kinetic())


    #Core Hamiltonian
    H = T + V

    S = np.array(mints.ao_overlap())
    g = np.array(mints.ao_eri())



    A = mints.ao_overlap()
    A.power(-0.5,1.e-14)
    A = np.array(A)


    def diag(F,A):
        Fp =A.T@F@A
        eps,cp = np.linalg.eigh(Fp)
        C=A@cp
        return eps,C
    eps, C = diag(H,A)
    Cocc = C[:,:nel]
    D = Cocc @ Cocc.T
    E_old = 0
    for iteration in range(25):
        J = np.einsum("pqrs,rs->pq",g,D)
        K = np.einsum("prqs,rs->pq",g,D)

        F = H + 2.0*J-K
            
        grad = F@D@S-S@D@F
        grad_rms = np.mean(grad **2) **0.5
        
        E_electric =  np.sum((F+H)*D)
        E_total= E_electric+mol.nuclear_repulsion_energy()
        E_diff=E_total-E_old
        E_old =E_total
        print("% 16.2f % 8.4e % 8.4e"%( E_total,E_diff, grad_rms))
        eps, C = diag(F,A)
        Cocc = C[:,:nel]
        D = Cocc @ Cocc.T

    print("SCF has finished!\n")
    return E_total
