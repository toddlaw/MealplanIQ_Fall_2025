import { Component, OnInit } from '@angular/core';

@Component({
  selector: 'app-carousel',
  templateUrl: './carousel.component.html',
  styleUrls: ['./carousel.component.css']
})
export class CarouselComponent implements OnInit {

  currentItem: number = 0;
  totalItems: number = 4;  // Adjust this to match the number of items in the carousel

  constructor() { }

  ngOnInit(): void { }

  updateCarousel(index: number) {
    this.currentItem = index;
  }

  goToNext() {
    this.currentItem = (this.currentItem + 1) % this.totalItems;
  }

  goToPrev() {
    this.currentItem = (this.currentItem - 1 + this.totalItems) % this.totalItems;
  }
}
