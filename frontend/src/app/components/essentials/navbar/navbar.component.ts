import { Component, OnInit } from '@angular/core';
import { AuthService } from 'src/app/services/auth.service';
import { HotToastService } from '@ngneat/hot-toast';
import { Router } from '@angular/router'; 

@Component({
  selector: 'app-navbar',
  templateUrl: './navbar.component.html',
  styleUrls: ['./navbar.component.css']
})
export class NavbarComponent implements OnInit {
  user$ = this.authService.currentUser$;
  public isMenuOpen: boolean = false;

  constructor(
    private authService: AuthService,
    private toast: HotToastService,
    private router: Router
  ) {}

  logout() {
    this.authService.logout().subscribe(() => {
      localStorage.removeItem('email');
      localStorage.removeItem('uid');
      this.toast.success('You have been logged out.');

      setTimeout(() => {
        window.location.replace('');
      }, 500);
    });
  }

  goToGenerateMealPlan() {
    this.router.navigate(['/generate'], {
      queryParams: { guest: 'true' }
    });
  }

  ngOnInit(): void {}
}
