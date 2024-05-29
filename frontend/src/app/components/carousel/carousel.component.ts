import { Component, OnInit } from '@angular/core';

@Component({
  selector: 'app-carousel',
  templateUrl: './carousel.component.html',
  styleUrls: ['./carousel.component.css']
})

export class CarouselComponent implements OnInit {

  currentItem: number = 0;
  totalItems: number = 4; 

  placeHolders = [
    {image:'1', file_name: 'assets/images/placeholders/placeholder_1.jpg'},
    {image: '2', file_name: 'assets/images/placeholders/placeholder_2.jpg'},
    {image:'3', file_name: 'assets/images/placeholders/placeholder_3.jpg'},
    {image: '4', file_name: 'assets/images/placeholders/placeholder_4.jpg'},
  ]

  constructor() { }

  ngOnInit(): void {
    this.setupCarousel();
  }

  setupCarousel(): void {
    const totalItems = this.placeHolders.length;
    setInterval(() => {
      this.goToNext()
    }, 3000); // change every 3 seconds

  }

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
