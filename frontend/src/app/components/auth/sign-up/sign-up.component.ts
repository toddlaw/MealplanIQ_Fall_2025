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
import { environment } from 'src/environments/environment';
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

  async submit() {
    const { name, email, password } = this.signUpForm.value;

    if (!this.signUpForm.valid || !name || !password || !email) {
      return;
    }

    try {
      const userCredential = await this.authService
        .signUp(email, password)
        .toPromise();
      console.log(userCredential);
      if (userCredential && userCredential.user) {
        localStorage.setItem('uid', userCredential.user.uid);
        localStorage.setItem('email', email);
      }

      const data = {
        user_id: userCredential?.user?.uid,
        user_name: name,
        email: email,
      };

      try {
        const response = await this.http
          .post(`${environment.baseUrl}/signup`, data)
          .toPromise();
        console.log(response);
        this.toast.observe({
          success: 'Congrats! You are all signed up',
          error: `Error: an error occurs during login`,
        }); // Show success toast
      } catch (error) {
        console.error(error);
      }

      this.router.navigate(['/']);
    } catch (Error) {
      const error = Error as Error;
      this.toast.error(`Error: ${error.message}`); // Show error toast
      console.error(error);
    }
  }

  showPassword = false;

  togglePasswordVisibility(event: Event) {
    event.preventDefault();
    this.showPassword = !this.showPassword;
  }
}
