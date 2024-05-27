import { Component, OnInit, ChangeDetectorRef } from '@angular/core';

@Component({
  selector: 'app-popup',
  templateUrl: './popup.component.html',
  styleUrls: ['./popup.component.css']
})
export class PopupComponent implements OnInit {
  showPopup: boolean = true;


  constructor(private cdr: ChangeDetectorRef) { }

  ngOnInit(): void {
    const hasVisited = localStorage.getItem('hasVisited');
    
    if (!hasVisited) {
      this.showPopup = true;
      localStorage.setItem('hasVisited', 'true');
    }
    console.log('hasVisited: ', this.showPopup);
    this.cdr.detectChanges();
  }

  closePopup(): void {
    this.showPopup = false;
  }
}
