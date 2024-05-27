import { Component, OnInit } from '@angular/core';

@Component({
  selector: 'app-popup',
  templateUrl: './popup.component.html',
  styleUrls: ['./popup.component.css']
})
export class PopupComponent implements OnInit {
  showPopup: boolean = true;

  constructor() { }

  ngOnInit(): void {
    // Show the popup when the component initializes
    this.showPopup = true;
  }

  closePopup() {
    this.showPopup = false;
  }
}
