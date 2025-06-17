import { Component, OnInit } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { environment } from 'src/environments/environment';


@Component({
  selector: 'app-popup',
  templateUrl: './popup.component.html',
  styleUrls: ['./popup.component.css']
})
export class PopupComponent implements OnInit {
  userSubscriptionTypeId: number = 0;
  showPopup: boolean = false;

  textValues = [
    {
      title: 'Join Today!',
      description: 'Join our community today to access exclusive functions and features.',
      button: 'Sign Up Now!'
    },
    {
      title: 'Subscribe Now!',
      description: 'Subscribe to our subscription plan to access exclusive functions and features.',
      button: 'Check out our plans!'
    }
  ];

  constructor(private http: HttpClient) {}

  ngOnInit() {
    this.checkUserSubscriptionType();
  }

  checkUserSubscriptionType(): void {
    const uid = localStorage.getItem('uid');
    if (!uid) {
      this.userSubscriptionTypeId = 0;
      return;
    }

    const stored = JSON.parse(localStorage.getItem('userProfile') || '{}').subscription_type_id;
    this.userSubscriptionTypeId = stored ? Number(stored) : 0;

    this.checkPopupStatus();
  }

  checkPopupStatus() {
    if (this.userSubscriptionTypeId === 0 || this.userSubscriptionTypeId === 1) {
      this.showPopup = true;
    } else {
      this.showPopup = false;
    }
  }

  closePopup() {
    this.showPopup = false;
  }

  getPopupContent() {
    if (this.userSubscriptionTypeId === 0) {
      return this.textValues[0];
    } else if (this.userSubscriptionTypeId === 1) {
      return this.textValues[1];
    }
    return null;
  }
}