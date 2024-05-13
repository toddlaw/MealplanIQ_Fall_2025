import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { HomeComponent } from './components/home/home.component';
import { LandingComponent } from './components/landing/landing.component';
import { LoginComponent } from './components/login/login.component';
import { SignUpComponent } from './components/sign-up/sign-up.component';
import { MissionComponent } from './components/mission/mission.component';
import { ApproachComponent } from './components/approach/approach.component';
import { ContactComponent } from './components/contact/contact.component';
import { LeadershipComponent } from './components/leadership/leadership.component';
import { PhilosophyComponent } from './components/philosophy/philosophy.component';
import { TechnologyComponent } from './components/technology/technology.component';
import { TimelineComponent } from './components/timeline/timeline.component';
import { SplashComponent } from './components/splash/splash.component';
import { Guard } from './services/guard.service'; // Import your guard here

import {
  canActivate,
  redirectLoggedInTo,
  redirectUnauthorizedTo,
} from '@angular/fire/auth-guard';
import { ProfileComponent } from './components/profile/profile.component';

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
    path: 'mission',
    component: MissionComponent,
  },
  {
    path: 'approach',
    component: ApproachComponent,
  },
  {
    path: 'contact',
    component: ContactComponent,
  },
  {
    path: 'leadership',
    component: LeadershipComponent,
  },
  {
    path: 'philosophy',
    component: PhilosophyComponent,
  },
  {
    path: 'technology',
    component: TechnologyComponent,
  },
  {
    path: 'timeline',
    component: TimelineComponent,
  },
  {
    path: 'splash',
    component: SplashComponent,
  },
];

@NgModule({
  declarations: [],
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule],
})
export class AppRoutingModule {}
