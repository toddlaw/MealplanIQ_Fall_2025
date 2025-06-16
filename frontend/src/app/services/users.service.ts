import { Injectable } from '@angular/core';
import { BehaviorSubject, Observable, tap } from 'rxjs';
import { ProfileUser } from '../models/user';
import { AuthService } from './auth.service';
import { environment } from 'src/environments/environment';
import { HttpClient } from '@angular/common/http';

@Injectable({
  providedIn: 'root',
})
export class UsersService {
  private profileSubject = new BehaviorSubject<any>(null);
  private preferenceSubject = new BehaviorSubject<any>(null);
  profile$ = this.profileSubject.asObservable();
  preference$ = this.preferenceSubject.asObservable();

  constructor(private authService: AuthService, private http: HttpClient) {}

  // Retrieve user data from back end and store in localStorage
  fetchAndStoreUserProfile(uid: string): Observable<any> {
    return this.http
      .get<any>(`${environment.baseUrl}/api/landing/profile/${uid}`)
      .pipe(
        tap((response) => {
          console.log(response)
          const { profile, preference } = response;
          if (profile) {
            localStorage.setItem('userProfile', JSON.stringify(profile));
            this.profileSubject.next(profile);
          }

          if (preference) {
            localStorage.setItem('userPreference', JSON.stringify(preference));
            this.preferenceSubject.next(preference);
          }
        })
      );
  }

  updateLocalUserProfile(profile: any) {
    localStorage.setItem('userProfile', JSON.stringify(profile));
    this.profileSubject.next(profile);
  }

  updateLocalUserPreference(preference: any) {
    localStorage.setItem('userPreference', JSON.stringify(preference));
    this.profileSubject.next(preference);
  }

  loadCachedUserProfile() {
    const profile = localStorage.getItem('userProfile');
    if (profile) {
      this.profileSubject.next(JSON.parse(profile));
    }

    const preference = localStorage.getItem('userPreference');
    if (preference) {
      this.preferenceSubject.next(JSON.parse(preference));
    }
  }
}
