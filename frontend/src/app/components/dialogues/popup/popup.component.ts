import { Component, OnInit, ChangeDetectorRef } from '@angular/core';

@Component({
  selector: 'app-popup',
  templateUrl: './popup.component.html',
  styleUrls: ['./popup.component.css']
})
export class PopupComponent implements OnInit {
  showPopup: boolean = false;

  ngOnInit(): void {  
    if (!localStorage.getItem('adShown')){
      this.showPopup = true;
      localStorage.setItem('adShown', 'true');
    }
  } 

  closePopup(): void {
    this.showPopup = false;
  }
}
