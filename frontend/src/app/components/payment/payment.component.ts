import { Component, OnInit } from '@angular/core';
import { AuthService } from 'src/app/services/auth.service';
import { environment } from 'src/environments/environment';

@Component({
  selector: 'app-payment',
  templateUrl: './payment.component.html',
  styleUrls: ['./payment.component.css'],
})
export class PaymentComponent implements OnInit {
  stripePublicKey!: string;
  stripePricingTableId!: string;
  userId!: string;
  userEmail!: string;

  constructor(private authService: AuthService) {}

  ngOnInit() {
      this.authService.currentUser$.subscribe((user) => {
        if (user) {
          this.userId = user.uid;
          this.userEmail = user.email ?? '';
        }
      });
    this.stripePublicKey = environment.stripePublicKey;
    this.stripePricingTableId = environment.stripePricingTableId;
  }
}

