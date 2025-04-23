import { Component, OnInit } from '@angular/core';
import { NonNullableFormBuilder, Validators } from '@angular/forms';
import {
  Auth,
  confirmPasswordReset,
  verifyPasswordResetCode,
} from '@angular/fire/auth';
import { ActivatedRoute, Router } from '@angular/router';
import { HotToastService } from '@ngneat/hot-toast';
import { passwordsMatchValidator } from '../sign-up/sign-up.component';

@Component({
  selector: 'app-reset-password',
  templateUrl: './reset-password.component.html',
  styleUrls: ['./reset-password.component.css'],
})
export class ResetPasswordComponent implements OnInit {
  resetPwForm = this.fb.group(
    {
      password: [
        '',
        [Validators.required, Validators.pattern(/^(?=.*[A-Z]).{8,}$/)],
      ],
      confirmPassword: ['', [Validators.required]],
    },
    { validators: passwordsMatchValidator() }
  );

  oobCode: string = '';
  email: string = '';
  errorMessage: string = '';
  showConfirmation: boolean = false;

  constructor(
    private fb: NonNullableFormBuilder,
    private auth: Auth,
    private route: ActivatedRoute,
    private router: Router,
    private toast: HotToastService
  ) {}

  ngOnInit(): void {
    this.oobCode = this.route.snapshot.queryParams['oobCode'];

    if (!this.oobCode) {
      this.errorMessage =
        'The reset link is invalid or has expired.<br>Please request a new link.';
    } else {
      this.verifyCode(this.oobCode);
    }
  }

  get password() {
    return this.resetPwForm.get('password');
  }

  get confirmPassword() {
    return this.resetPwForm.get('confirmPassword');
  }

  // verify the reset link
  verifyCode(oobCode: string) {
    verifyPasswordResetCode(this.auth, oobCode)
      .then((email) => {
        this.email = email;
      })
      .catch((error) => {
        console.log('Error in verifying reset code: ', error);
        this.errorMessage =
          'The reset link is invalid or has expired. <br> Please request a new link.';
      });
  }

  submit() {
    const { password, confirmPassword } = this.resetPwForm.value;

    if (!this.resetPwForm.valid || !password || !confirmPassword) {
      return;
    }

    const toastRef = this.toast.loading('Resetting your password...');

    // change pwd through Firebase
    confirmPasswordReset(this.auth, this.oobCode, password!).then(() => {
      toastRef.close();
      this.showConfirmation = true;
    });
  }

  showPassword = false;

  togglePasswordVisibility(event: Event) {
    event.preventDefault();
    this.showPassword = !this.showPassword;
  }
}
