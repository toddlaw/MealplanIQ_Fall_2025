import { Component, OnInit } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import {
  AbstractControl,
  FormControl,
  FormGroup,
  NonNullableFormBuilder,
  ValidationErrors,
  ValidatorFn,
  Validators,
} from '@angular/forms';
import { Router } from '@angular/router';
import { HotToastService } from '@ngneat/hot-toast';
import { switchMap } from 'rxjs/operators';
import { AuthService } from 'src/app/services/auth.service';
// import { UsersService } from 'src/app/services/users.service';

export function passwordsMatchValidator(): ValidatorFn {
  return (control: AbstractControl): ValidationErrors | null => {
    const password = control.get('password')?.value;
    const confirmPassword = control.get('confirmPassword')?.value;

    if (password && confirmPassword && password !== confirmPassword) {
      return { passwordsDontMatch: true };
    } else {
      return null;
    }
  };
}

@Component({
  selector: 'app-sign-up',
  templateUrl: './sign-up.component.html',
  styleUrls: ['./sign-up.component.css'],
})
export class SignUpComponent implements OnInit {
  signUpForm = this.fb.group(
    {
      name: ['', Validators.required],
      email: ['', [Validators.required, Validators.email]],
      password: [
        '',
        [Validators.required, Validators.pattern(/^(?=.*[A-Z]).{8,}$/)],
      ],
      confirmPassword: ['', Validators.required],
    },
    { validators: passwordsMatchValidator() }
  );

  constructor(
    private authService: AuthService,
    private router: Router,
    private toast: HotToastService,
    private http: HttpClient,
    private fb: NonNullableFormBuilder
  ) {}

  ngOnInit(): void {}

  get email() {
    return this.signUpForm.get('email');
  }

  get password() {
    return this.signUpForm.get('password');
  }

  get confirmPassword() {
    return this.signUpForm.get('confirmPassword');
  }

  get name() {
    return this.signUpForm.get('name');
  }

  submit() {
    const { name, email, password } = this.signUpForm.value;

    if (!this.signUpForm.valid || !name || !password || !email) {
      return;
    }

    this.authService.signUp(email, password).subscribe({
      next: (userCredential) => {
        console.log(userCredential);
        localStorage.setItem('uid', userCredential.user.uid);
        const data = {
          user_id: userCredential.user.uid,
          user_name: name,
          email: email,
        };

        const data2 = {
          user_id: userCredential.user.uid 
        }
        this.http.post('http://127.0.0.1:5000/get_subscription_type', { params: data2 }).subscribe({
          next: (response) => {
            console.log(response);
          }
        });
        this.http.post('http://127.0.0.1:5000/signup', data).subscribe({
          next: (response) => {
            console.log(response);
            this.toast.observe({
              success: 'Congrats! You are all signed up',
              error: `Error: an error occurs during login`,
            }); // Show success toast
          },
          error: (error) => {
            console.error(error);
          },
        });
        this.router.navigate(['/']);
      },
      error: (Error) => {
        this.toast.error(`Error: ${Error.message}`); // Show error toast
        console.error(Error);
      },
    });
  }
  showPassword = false;

  togglePasswordVisibility(event: Event) {
    event.preventDefault();
    this.showPassword = !this.showPassword;
  }
}
