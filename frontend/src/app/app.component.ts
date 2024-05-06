import { Component } from '@angular/core';
import { Router } from '@angular/router';
import { AuthService } from './services/auth.service';
import { UsersService } from './services/users.service';
import { MatIconRegistry } from '@angular/material/icon';
import { DomSanitizer } from '@angular/platform-browser';

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.scss'],
})
export class AppComponent {
  user$ = this.usersService.currentUserProfile$;
  public isMenuOpen: boolean = false;

  constructor(
    private authService: AuthService,
    public usersService: UsersService,
    private router: Router, 
    private matIconRegistry: MatIconRegistry,
    private domSanitizer: DomSanitizer
  ) {
    this.matIconRegistry.addSvgIcon(
      'liked-foods',
      this.domSanitizer.bypassSecurityTrustResourceUrl('../assets/images/liked-foods.svg')
    );    
    this.matIconRegistry.addSvgIcon(
      'disliked-foods',
      this.domSanitizer.bypassSecurityTrustResourceUrl('../assets/images/disliked-foods.svg')
    );    
    this.matIconRegistry.addSvgIcon(
      'people',
      this.domSanitizer.bypassSecurityTrustResourceUrl('../assets/images/people.svg')
    );    
    this.matIconRegistry.addSvgIcon(
      'religious',
      this.domSanitizer.bypassSecurityTrustResourceUrl('../assets/images/religious.svg')
    );    
  } 

  logout() {
    this.authService.logout().subscribe(() => {
      this.router.navigate(['/']);
    });
  }

  public onSidenavClick(): void {
    this.isMenuOpen = false;
  }
}
