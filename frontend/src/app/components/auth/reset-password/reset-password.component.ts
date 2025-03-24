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
import { firstValueFrom } from 'rxjs';

@Component({
  selector: 'app-reset-password',
  templateUrl: './reset-password.component.html',
  styleUrls: ['./reset-password.component.css'],
})
export class ResetPasswordComponent implements OnInit {
  resetPwForm = this.fb.group({
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
    return this.resetPwForm.get('email');
  }

  submit() {
    const email = this.resetPwForm.get('email')?.value;

    if (!this.resetPwForm.valid || !email) {
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
    this.countdown = 60;
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
