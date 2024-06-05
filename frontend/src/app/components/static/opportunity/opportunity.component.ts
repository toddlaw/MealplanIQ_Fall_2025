import { Component, OnInit } from '@angular/core';

@Component({
  selector: 'app-opportunity',
  templateUrl: './opportunity.component.html',
  styleUrls: ['./opportunity.component.css']
})
export class OpportunityComponent implements OnInit {


  Team = [
    {'department': 'Executive', 'position': 'Founder & CEO', 'name': 'Warren', 
    'image': 'assets/images/image-placeholder.png',
    'description': 'Warren, the founder of MealPlanIQ and the CEO of Galapagos Technologies Incorporated, has 30 years of experience in the software engineering field, along with 10 years in Artificial Intelligence. He holds a Bachelor’s degree in Electrical Engineering and a PhD in Computer Science, bringing a wealth of knowledge and expertise to his ventures.' },
    {'department': 'Domain Expert', 'position': 'Registered Dietitian', 'name': 'Rachelle', 
    'image': 'assets/images/image-placeholder.png',
    'description':'Rachelle is a Certified Personal Trainer who helps with providing insights about personalized meal plans.'},
    {'department': 'Development', 'position': 'Project Manager', 'name': 'Jose', 
    'image': 'assets/images/image-placeholder.png',
    'description':'Jose has 25 years in project management.'}
  ]

  constructor() { }

  ngOnInit(): void {
  }

}
