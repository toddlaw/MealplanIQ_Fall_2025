import { Component, OnInit } from '@angular/core';
import { NonNullableFormBuilder, Validators } from '@angular/forms';
import { HotToastService } from '@ngneat/hot-toast';
import { AuthService } from 'src/app/services/auth.service';

@Component({
  selector: 'app-forgot-password',
  templateUrl: './forgot-password.component.html',
  styleUrls: ['./forgot-password.component.css'],
})
export class ForgotPasswordComponent implements OnInit {
  forgotPwForm = this.fb.group({
    email: ['', [Validators.required, Validators.email]],
  });

  showConfirmation: boolean = false;
  countdown: number = 60;
  timer: any;
  resendAvailable: boolean = false;
  emailToResend: string = '';

  constructor(
    private fb: NonNullableFormBuilder,
    private toast: HotToastService,
    private authService: AuthService
  ) {}

  ngOnInit(): void {}

  get email() {
    return this.forgotPwForm.get('email');
  }

  submit() {
    const email = this.forgotPwForm.get('email')?.value;

    if (!this.forgotPwForm.valid || !email) {
      return;
    }

    const toastRef = this.toast.loading('Sending password reset email...');

    this.authService
      .resetPassword(email)
      .then(() => {
        toastRef.close();
        this.emailToResend = email;
        this.showConfirmation = true;
        this.startCountdown();
      })
      .catch((error) => {
        toastRef.close();
        if (error.code === 'auth/invalid-email') {
          this.toast.error(
            'Invalid email. Please check the email address and try again.'
          );
        } else {
          this.toast.error(
            'Unable to send reset email. Please try again later.'
          );
        }
      });
  }

  startCountdown() {
    this.countdown = 10;
    this.resendAvailable = false;
    this.timer = setInterval(() => {
      this.countdown--;
      if (this.countdown <= 0) {
        this.resendAvailable = true;
        clearInterval(this.timer);
      }
    }, 1000);
  }

  resendEmail() {
    if (!this.resendAvailable || !this.emailToResend) return;

    const toastRef = this.toast.loading('Resending password reset email...');

    this.authService
      .resetPassword(this.emailToResend)
      .then(() => {
        toastRef.close();
        this.toast.success('The password reset email has been resent.');
        this.startCountdown();
      })
      .catch(() => {
        toastRef.close();
        this.toast.error('Failed to resend. Please try again later.');
      });
  }
}
