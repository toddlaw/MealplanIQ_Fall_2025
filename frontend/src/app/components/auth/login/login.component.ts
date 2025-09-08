import { Component, OnInit } from '@angular/core';
import { NonNullableFormBuilder, Validators } from '@angular/forms';
import { Router } from '@angular/router';
import { HotToastService } from '@ngneat/hot-toast';
import { AuthService } from 'src/app/services/auth.service';
import { HttpClient } from '@angular/common/http';
import { UsersService } from 'src/app/services/users.service';

@Component({
  selector: 'app-login',
  templateUrl: './login.component.html',
  styleUrls: ['./login.component.css'],
})
export class LoginComponent implements OnInit {
  loginForm = this.fb.group({
    email: ['', [Validators.required, Validators.email]],
    password: ['', Validators.required],
  });

  constructor(
    private authService: AuthService,
    private toast: HotToastService,
    private router: Router,
    private fb: NonNullableFormBuilder, // private usersService: UsersService
    private http: HttpClient,
    private usersService: UsersService
  ) {}

  ngOnInit(): void {}

  get email() {
    return this.loginForm.get('email');
  }

  get password() {
    return this.loginForm.get('password');
  }

  submit() {
    const { email, password } = this.loginForm.value;

    if (!this.loginForm.valid || !email || !password) {
      return;
    }

    this.authService
      .login(email, password)
      .pipe(
        this.toast.observe({
          success: 'Logged in successfully',
          loading: 'Logging in...',
          error: () =>
            `There was an error: Please check your email and password and try again. `,
        })
      )
      .subscribe((userCredential) => {
        const { user } = userCredential; // Extracting user information from UserCredential
        if (user) {
          localStorage.setItem('email', user.email || '');
          localStorage.setItem('uid', user.uid);

          this.usersService.fetchAndStoreUserProfile(user.uid).subscribe({
            next: () => {
              this.router.navigate(['/dashboard']);
            },
            error: (err) => {
              console.error('Failed to fetch user profile:', err);
              this.router.navigate(['/dashboard']);
            },
          });
        } else {
          console.error('User is null');
        }

        this.router.navigate(['/dashboard']);
      });
  }
  showPassword = false;

  togglePasswordVisibility(event: Event) {
    event.preventDefault();
    this.showPassword = !this.showPassword;
  }
}
