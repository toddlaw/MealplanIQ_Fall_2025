/**
 * CarouselComponent is an Angular component that displays a carousel of images.
 * It allows users to navigate through a series of images with titles and subtitles.
 * 
 * @author
 */

import { Component, OnInit, Input } from '@angular/core';

@Component({
  selector: 'app-carousel',
  templateUrl: './carousel.component.html',
  styleUrls: ['./carousel.component.css'],
})
export class CarouselComponent implements OnInit {
  @Input() imgClass: string = '';
  @Input() containerClass: string = '';
  @Input() extraClass: string = '';
  currentItem: number = 0;
  totalItems: number = 13;

  placeHolders = [
    {
      file_name: 'assets/images/placeholders/carousel1.jpg',
      title: 'Fight cancer',
      subtitle: '',
    },
    {
      file_name: 'assets/images/placeholders/carousel2.jpg',
      title: 'Fight heart disease',
      subtitle: '',
    },
    {
      file_name: 'assets/images/placeholders/carousel3.jpg',
      title: 'Fight diabetes',
      subtitle: '',
    },
    {
      file_name: 'assets/images/placeholders/carousel4.jpg',
      title: 'Fight obesity',
      subtitle: '',
    },
    {
      file_name: 'assets/images/placeholders/carousel5.jpg',
      title: '...or build muscle',
      subtitle: '',
    },
    {
      file_name: 'assets/images/placeholders/carousel6.jpg',
      title: '... with personalized meal plans',
      subtitle: '',
    },
    {
      file_name: 'assets/images/placeholders/carousel7.jpg',
      title: 'designed by a registered dietitian',
      subtitle: '',
    },
    {
      file_name: 'assets/images/placeholders/carousel8.jpg',
      title: 'and meet government dietary guidelines',
      subtitle: '',
    },
    {
      file_name: 'assets/images/placeholders/carousel9.jpg',
      title: 'automatically generated and sent to your inbox',
      subtitle: '',
    },
    {
      file_name: 'assets/images/placeholders/carousel10.jpg',
      title: 'selecting food for you want to eat',
      subtitle: '',
    },
    {
      file_name: 'assets/images/placeholders/carousel11.jpg',
      title: 'optimizing for your preferences and health goals',
      subtitle: '',
    },
    {
      file_name: 'assets/images/placeholders/carousel12.jpg',
      title: 'all for less than $10 a month',
      subtitle: '',
    },
    {
      file_name: 'assets/images/placeholders/carousel3.jpg',
      title: 'and now free for our weight-loss plan members!',
      subtitle: '',
    },
  ];

  constructor() {}

  ngOnInit(): void {
    this.setupCarousel();
  }

  setupCarousel(): void {
    const totalItems = this.placeHolders.length;
    setInterval(() => {
      this.goToNext();
    }, 4000); // change every 3 seconds
  }

  updateCarousel(index: number) {
    this.currentItem = index;
  }

  goToNext() {
    this.currentItem = (this.currentItem + 1) % this.totalItems;
  }

  goToPrev() {
    this.currentItem =
      (this.currentItem - 1 + this.totalItems) % this.totalItems;
  }
}
