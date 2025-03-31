import { Component, OnInit, Input } from '@angular/core';

@Component({
  selector: 'app-carousel',
  templateUrl: './carousel.component.html',
  styleUrls: ['./carousel.component.css']
})

export class CarouselComponent implements OnInit {
  @Input() imgClass: string = ''; 
  @Input() containerClass: string = '';
  @Input() extraClass: string = '';
  currentItem: number = 0;
  totalItems: number = 13; 

  placeHolders = [
    {image:'1', file_name: 'assets/images/placeholders/placeholder_1.png'},
    {image: '2', file_name: 'assets/images/placeholders/placeholder_2.png'},
    {image:'3', file_name: 'assets/images/placeholders/placeholder_3.png'},
    {image: '4', file_name: 'assets/images/placeholders/placeholder_4.png'},
    {image: '5', file_name: 'assets/images/placeholders/placeholder_5.png'},
    {image: '6', file_name: 'assets/images/placeholders/placeholder_6.png'},
    {image: '7', file_name: 'assets/images/placeholders/placeholder_7.png'},
    {image: '8', file_name: 'assets/images/placeholders/placeholder_8.png'},
    {image: '9', file_name: 'assets/images/placeholders/placeholder_9.png'},
    {image: '10', file_name: 'assets/images/placeholders/placeholder_10.png'},
    {image: '11', file_name: 'assets/images/placeholders/placeholder_11.png'},
    {image: '12', file_name: 'assets/images/placeholders/placeholder_12.png'},
    {image: '13', file_name: 'assets/images/placeholders/placeholder_13.png'},
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
