import { Component, OnInit } from '@angular/core';
import { environment } from 'src/environments/environment';

@Component({
  selector: 'app-intro',
  templateUrl: './intro.component.html',
  styleUrls: ['./intro.component.css'],
})
export class IntroComponent implements OnInit {
  constructor() {}

  ngOnInit(): void {}

  goToQuestionnaire() {
    window.location.href = environment.questionnaireUrl;
  }
}
