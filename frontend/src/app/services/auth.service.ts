import { Injectable } from '@angular/core';
import { HotToastService } from '@ngneat/hot-toast';
import {
  Auth,
  signInWithEmailAndPassword,
  authState,
  createUserWithEmailAndPassword,
  UserCredential,
} from '@angular/fire/auth';
import { concatMap, from, Observable, of, switchMap } from 'rxjs';

@Injectable({
  providedIn: 'root',
})
export class AuthService {
  currentUser$ = authState(this.auth);

  constructor(private auth: Auth, private toast: HotToastService) {}

  signUp(email: string, password: string): Observable<UserCredential> {
    
    return from(createUserWithEmailAndPassword(this.auth, email, password));
  }

  login(email: string, password: string): Observable<any> {
    return from(signInWithEmailAndPassword(this.auth, email, password));
  }

  logout(): Observable<any> {
    localStorage.removeItem('uid');
    // localStorage.removeItem('email');
    localStorage.clear();
    this.toast.success('You have been logged out.');
    return from(this.auth.signOut());
  }
}
