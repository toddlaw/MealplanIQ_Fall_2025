import { Injectable } from '@angular/core';
import { CanActivate, Router } from '@angular/router';
import { Observable } from 'rxjs';
import { tap } from 'rxjs/operators';
import { HotToastService } from '@ngneat/hot-toast';

@Injectable({
  providedIn: 'root',
})
export class Guard implements CanActivate {
  constructor(private router: Router, private toast: HotToastService) {}

  canActivate(): Observable<boolean> | boolean {
    const isAuthorized = this.checkAuthorizationLogic(); // Implement your authorization logic here

    if (!isAuthorized) {
      // Display a warning toast message
      this.toast.warning('You need to be logged in to access this page.');
      this.router.navigate(['/login']); // Redirect to the login page
    }

    return isAuthorized; // Allow or prevent redirection based on authorization status
  }

  private checkAuthorizationLogic(): boolean {
    // Implement your authorization logic here
    // Return true if the user is authorized, otherwise return false
    if (localStorage.getItem('uid')) {
      return true;
    } else {
      return false;
    }
  }
}
