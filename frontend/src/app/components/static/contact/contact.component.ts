import { Component, OnInit } from '@angular/core';
import { FormGroup, FormBuilder, Validator, Validators } from '@angular/forms';
import { Subject } from 'rxjs';

@Component({
  selector: 'app-contact',
  templateUrl: './contact.component.html',
  styleUrls: ['./contact.component.css']
})
export class ContactComponent implements OnInit {
  contactForm: FormGroup;

  SubjectOptions = [
    {'value': 'general_inquiry', 'subject': 'General Inquiry'},
    {'value': 'support', 'subject': 'Support'},
    {'value': 'feedback', 'subject': 'Feedback'},
    {'value': 'opportunity', 'subject': 'Opportunity'},
    {'value': 'other', 'subject': 'Other'},
  ]

  constructor(private fb: FormBuilder) {
    this.contactForm = this.fb.group({
      name: ['', Validators.required], 
      email: ['', [Validators.required, Validators.email]], 
      subject: ['', Validators.required], 
      message: ['', Validators.required]
    })
   }

   onSubmit() {
    if (this.contactForm.valid){
      console.log('Form submitted', this.contactForm.value);
      //
    } else {
    console.log('unsucessful');
   }
  }
  
  ngOnInit(): void {
  }

}
