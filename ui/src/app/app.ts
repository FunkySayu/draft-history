import { Component } from '@angular/core';
import { Echo as EchoComponent } from './components/echo/echo';
// HttpClientModule is now typically provided in app.config.ts or bootstrapApplication
// BrowserAnimationsModule is also typically handled in app.config.ts or via provideAnimations()

@Component({
  selector: 'app-root',
  standalone: true, // Ensuring standalone is true, as is common with newer Angular versions
  imports: [
    EchoComponent
    // No RouterOutlet as routing=false
  ],
  template: `
    <div style="text-align:center" class="content">
      <h1>League Pick Rate History</h1>
    </div>
    <app-echo></app-echo>
  `,
  styles: [],
})
export class App {
  title = 'ui'; // Removed protected to match common practice, though not strictly necessary
}
