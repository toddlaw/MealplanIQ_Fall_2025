import { Component, OnInit } from '@angular/core';
import { environment } from 'src/environments/environment';

@Component({
  selector: 'app-payment',
  templateUrl: './payment.component.html',
  styleUrls: ['./payment.component.css'],
})
export class PaymentComponent implements OnInit {
  stripePublicKey!: string;
  stripePricingTableId!: string;

  constructor() {}

  ngOnInit() {
    this.stripePublicKey = environment.stripePublicKey;
    this.stripePricingTableId = environment.stripePricingTableId;
  }
}
