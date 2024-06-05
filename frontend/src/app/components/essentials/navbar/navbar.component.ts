import { Component, OnInit } from '@angular/core';
import { AuthService } from 'src/app/services/auth.service';
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
    private router: Router
  ) { }

  logout() {
    this.authService.logout().subscribe(() => {
      localStorage.removeItem('email');
      localStorage.removeItem('uid');
      this.router.navigate(['/']);
    });
  }

  ngOnInit(): void {
  }
}
