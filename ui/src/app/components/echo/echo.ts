import { Component } from '@angular/core';
import { Echo as EchoService } from '../../services/echo'; // Renamed to avoid conflict
import { FormsModule } from '@angular/forms'; // For ngModel
import { MatInputModule } from '@angular/material/input';
import { MatButtonModule } from '@angular/material/button';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatCardModule } from '@angular/material/card';
import { CommonModule } from '@angular/common'; // For async pipe and ngIf

@Component({
  selector: 'app-echo',
  standalone: true, // Ensure this is present if your CLI version adds it by default
  imports: [
    FormsModule,
    MatInputModule,
    MatButtonModule,
    MatFormFieldModule,
    MatCardModule,
    CommonModule
  ],
  template: `
    <mat-card>
      <mat-card-header>
        <mat-card-title>Echo Service</mat-card-title>
      </mat-card-header>
      <mat-card-content>
        <mat-form-field appearance="fill">
          <mat-label>Enter message</mat-label>
          <textarea matInput [(ngModel)]="messageToSend" placeholder="Type your message here"></textarea>
        </mat-form-field>
        <button mat-raised-button color="primary" (click)="sendMessage()">Send</button>

        <div *ngIf="response" style="margin-top: 20px;">
          <h3>Response:</h3>
          <pre>{{ response | json }}</pre>
        </div>
        <div *ngIf="error" style="margin-top: 20px; color: red;">
          <h3>Error:</h3>
          <pre>{{ error | json }}</pre>
        </div>
      </mat-card-content>
    </mat-card>
  `,
  styles: [`
    mat-card {
      max-width: 600px;
      margin: 20px auto;
    }
    mat-form-field {
      width: 100%;
    }
    button {
      margin-top: 10px;
    }
  `]
})
export class Echo { // Component class name
  messageToSend: string = '';
  response: any = null;
  error: any = null;

  constructor(private echoService: EchoService) { } // Service injected

  sendMessage(): void {
    this.response = null;
    this.error = null;
    this.echoService.sendEcho(this.messageToSend).subscribe({
      next: (res) => this.response = res,
      error: (err) => this.error = err
    });
  }
}
