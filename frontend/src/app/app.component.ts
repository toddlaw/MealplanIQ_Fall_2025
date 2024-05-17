import { Component, AfterViewInit } from '@angular/core';
import { Router } from '@angular/router';
import { AuthService } from './services/auth.service';
// import { UsersService } from './services/users.service';
import { MatIconRegistry } from '@angular/material/icon';
import { DomSanitizer } from '@angular/platform-browser';

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.css'],
})
export class AppComponent implements AfterViewInit {
  user$ = this.authService.currentUser$;
  public isMenuOpen: boolean = false;

  constructor(
    private authService: AuthService,
    // public usersService: UsersService,
    private router: Router,
    private matIconRegistry: MatIconRegistry,
    private domSanitizer: DomSanitizer
  ) {
    this.matIconRegistry.addSvgIcon(
      'liked-foods',
      this.domSanitizer.bypassSecurityTrustResourceUrl(
        '../assets/images/liked-foods.svg'
      )
    );
    this.matIconRegistry.addSvgIcon(
      'disliked-foods',
      this.domSanitizer.bypassSecurityTrustResourceUrl(
        '../assets/images/disliked-foods.svg'
      )
    );
    this.matIconRegistry.addSvgIcon(
      'people',
      this.domSanitizer.bypassSecurityTrustResourceUrl(
        '../assets/images/people.svg'
      )
    );
    this.matIconRegistry.addSvgIcon(
      'religious',
      this.domSanitizer.bypassSecurityTrustResourceUrl(
        '../assets/images/religious.svg'
      )
    );
  }

  ngAfterViewInit(): void {
    // code will execution after DOM rendered
    this.adjustContent();
  }

  logout() {
    this.authService.logout().subscribe(() => {
      localStorage.removeItem('email');
      localStorage.removeItem('uid');
      this.router.navigate(['/']);
    });
  }

  public onSidenavClick(): void {
    this.isMenuOpen = false;
  }

  adjustContent(): void {
    var contentDiv = document.getElementsByClassName(
      'mat-sidenav-content'
    )[0] as HTMLElement;
    var windowHeight = window.innerHeight;
    if (contentDiv.offsetHeight < windowHeight - 64) {
      contentDiv.style.height = `${windowHeight - 64}px`;
    }
  }
}
