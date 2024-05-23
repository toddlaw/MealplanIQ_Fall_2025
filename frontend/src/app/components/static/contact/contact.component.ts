import { Component, OnInit } from '@angular/core';
import { FormGroup, FormBuilder, Validator, Validators } from '@angular/forms';
import { ContactService } from './contact.service'

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

  constructor(private fb: FormBuilder, private contactService: ContactService) {
    this.contactForm = this.fb.group({
      name: ['', Validators.required], 
      email: ['', [Validators.required, Validators.email]], 
      subject: ['', Validators.required], 
      message: ['', Validators.required]
    })
   }

   onSubmit(): void {
    if (this.contactForm.valid){
      this.contactService.sendEmail(this.contactForm.value).subscribe(
        response => {
          alert('Form submitted')
        }, error => {
          console.error('Error Sending email', error)
        }
      );
    }
  }
  
  ngOnInit(): void {
  }

}
