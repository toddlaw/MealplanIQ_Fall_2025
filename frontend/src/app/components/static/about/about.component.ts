import { Component, OnInit } from '@angular/core';

@Component({
  selector: 'app-about',
  templateUrl: './about.component.html',
  styleUrls: ['./about.component.css']
})
export class AboutComponent implements OnInit {

  constructor() { }

  Philosophy = [
    {'image': 'assets/images/placeholders/philosophy_1.jpg', 'text': 'We believe deciding what to cook and eat is a highly personal decision, and dependent on many factors including age, weight, activity levels, religion, allergies, cuisine preferences, cooking skills, and health goals.'},
    {'image': 'assets/images/placeholders/philosophy_2.jpg', 'text': 'We believe that food can fight cancer, heart disease, Alzheimer’s, diabetes, and other conditions.'},
    {'image': 'assets/images/placeholders/philosophy_3.jpg', 'text': 'We believe in proven science technology, not gimmicks or shortcuts. We believe AI can be used to generate personalized meal plans which meet many constraints.'},
    {'image': 'assets/images/placeholders/philosophy_4.jpg', 'text': 'We believe that creating meal plans should be as easy as booking a plane ticket or a hotel room!'},
    {'image': 'assets/images/placeholders/philosophy_5.jpg', 'text': 'We believe in government guidelines (such as the United States’ USDA dietary recommendations) and the expertise of registered dietitians as a baseline for meal plans.'}
  ]

  ngOnInit(): void {
  }

}
