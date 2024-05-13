import { NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';
import { AppComponent } from './app.component';
import { BrowserAnimationsModule } from '@angular/platform-browser/animations';
import { AppRoutingModule } from './app-routing.module';
import { LoginComponent } from './components/login/login.component';
import { SignUpComponent } from './components/sign-up/sign-up.component';
import { HomeComponent } from './components/home/home.component';
import { MatToolbarModule } from '@angular/material/toolbar';
import { MatIconModule } from '@angular/material/icon';
import { MatButtonModule } from '@angular/material/button';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { ReactiveFormsModule, FormGroup } from '@angular/forms';
import { initializeApp, provideFirebaseApp } from '@angular/fire/app';
import { environment } from '../environments/environment';
import { provideAuth, getAuth } from '@angular/fire/auth';
import { provideFirestore, getFirestore } from '@angular/fire/firestore';
import { HotToastModule } from '@ngneat/hot-toast';
import { LandingComponent } from './components/landing/landing.component';
import { TermsAndConditionsComponent } from './components/tac-dialog/tac-dialog.component';
import { MatMenuModule } from '@angular/material/menu';
import { ProfileComponent } from './components/profile/profile.component';
// import { getStorage, provideStorage } from '@angular/fire/storage';
import { MatRadioModule } from '@angular/material/radio';
import { MatCardModule } from '@angular/material/card';
import { MatSelectModule } from '@angular/material/select';
import { MatDatepickerModule } from '@angular/material/datepicker';
import { MatNativeDateModule } from '@angular/material/core';
import { FormsModule } from '@angular/forms';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { HttpClientModule } from '@angular/common/http';
import { MatListModule } from '@angular/material/list';
import { MatExpansionModule } from '@angular/material/expansion';
import { MatButtonToggleModule } from '@angular/material/button-toggle';
import { OverlayModule } from '@angular/cdk/overlay';
import { MatTableModule } from '@angular/material/table';
import { MatDialogModule } from '@angular/material/dialog';
import { MatSidenavModule } from '@angular/material/sidenav';
import { MissionComponent } from './components/mission/mission.component';
import { PhilosophyComponent } from './components/philosophy/philosophy.component';
import { ApproachComponent } from './components/approach/approach.component';
import { TechnologyComponent } from './components/technology/technology.component';
import { LeadershipComponent } from './components/leadership/leadership.component';
import { TimelineComponent } from './components/timeline/timeline.component';
import { ContactComponent } from './components/contact/contact.component';
import { SplashComponent } from './components/splash/splash.component';

import { ShoppingListComponent } from './components/dialogues/shopping-list/shopping-list.component';

@NgModule({
  declarations: [
    AppComponent,
    LoginComponent,
    SignUpComponent,
    LandingComponent,
    HomeComponent,
    ProfileComponent,
    TermsAndConditionsComponent,
    MissionComponent,
    PhilosophyComponent,
    ApproachComponent,
    TechnologyComponent,
    LeadershipComponent,
    TimelineComponent,
    ContactComponent,
    SplashComponent,
    ShoppingListComponent,
  ],
  imports: [
    BrowserModule,
    MatProgressSpinnerModule,
    BrowserAnimationsModule,
    AppRoutingModule,
    MatToolbarModule,
    MatIconModule,
    MatButtonModule,
    MatCardModule,
    MatListModule,
    MatFormFieldModule,
    MatInputModule,
    ReactiveFormsModule,
    FormsModule,
    MatExpansionModule,
    MatButtonToggleModule,
    OverlayModule,
    provideFirebaseApp(() => initializeApp(environment.firebase)),
    provideAuth(() => getAuth()),
    // provideFirestore(() => getFirestore()),
    // provideStorage(() => getStorage()),
    HotToastModule.forRoot(),
    MatMenuModule,
    MatRadioModule,
    MatSelectModule,
    MatDatepickerModule,
    MatNativeDateModule,
    HttpClientModule,
    MatTableModule,
    MatDialogModule,
    MatSidenavModule,
  ],
  providers: [],
  bootstrap: [AppComponent],
})
export class AppModule {}
