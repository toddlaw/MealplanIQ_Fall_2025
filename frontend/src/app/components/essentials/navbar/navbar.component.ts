import { Component, OnInit } from '@angular/core';
import { AuthService } from 'src/app/services/auth.service';
import { HotToastService } from '@ngneat/hot-toast';

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
    private toast: HotToastService
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

  ngOnInit(): void {}
}
