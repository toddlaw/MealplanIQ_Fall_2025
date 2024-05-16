import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { HomeComponent } from './components/home/home.component';
import { LandingComponent } from './components/landing/landing.component';
import { LoginComponent } from './components/auth/login/login.component';
import { SignUpComponent } from './components/auth/sign-up/sign-up.component';
import { AboutComponent } from './components/static/about/about.component';
import { ContactComponent } from './components/static/contact/contact.component';
import { SplashComponent } from './components/splash/splash.component';
import { Guard } from './services/guard.service'; // Import your guard here

import {
  canActivate,
  redirectLoggedInTo,
  redirectUnauthorizedTo,
} from '@angular/fire/auth-guard';
import { ProfileComponent } from './components/profile/profile.component';
import { TermsAndConditionsComponent } from './components/dialogues/tac-dialog/tac-dialog.component';
import { PrivacyComponent } from './components/static/privacy/privacy.component';
import { OpportunityComponent } from './components/static/opportunity/opportunity.component';

const redirectUnauthorizedToLogin = () => redirectUnauthorizedTo(['login']);
const redirectLoggedInToLanding = () => redirectLoggedInTo(['']);

const routes: Routes = [
  {
    path: '',
    pathMatch: 'full',
    component: LandingComponent,
  },
  {
    path: 'login',
    component: LoginComponent,
    // ...canActivate(redirectLoggedInToLanding),
  },
  {
    path: 'sign-up',
    component: SignUpComponent,
    // ...canActivate(redirectLoggedInToLanding),
  },
  {
    path: 'home',
    component: HomeComponent,
    // ...canActivate(redirectUnauthorizedToLogin),
  },
  {
    path: 'profile',
    component: ProfileComponent,
    canActivate: [Guard],
  },
  {
    path: 'about',
    component: AboutComponent,
  },
  {
    path: 'contact',
    component: ContactComponent,
  },
  {
    path: 'splash',
    component: SplashComponent,
  },
  {
    path: 'privacy',
    component: PrivacyComponent,
  },
  {
    path: 'opportunity',
    component: OpportunityComponent,
  }
];

@NgModule({
  declarations: [],
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule],
})
export class AppRoutingModule {}
