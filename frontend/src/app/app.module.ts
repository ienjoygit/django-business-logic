import { NgModule, ApplicationRef } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';
import { FormsModule } from '@angular/forms';
import { HttpModule } from '@angular/http';
import { RouterModule } from '@angular/router';
import { removeNgStyles, createNewHosts, createInputTransfer } from '@angularclass/hmr';

/*
 * Platform and Environment providers/directives/pipes
 */
import { ENV_PROVIDERS } from './environment';
import { ROUTES } from './app.routes';
// App is our top level component
import { App } from './app.component';
import { APP_RESOLVER_PROVIDERS } from './app.resolver';
import { AppState, InternalStateType } from './app.service';

import { RestService } from "./services/rest.service";

import { BlocklyComponent } from './components/blockly/blockly.component';
import { BreadcrumbComponent } from './components/breadcrumb.component';

import { NoContentComponent } from './components/no-content/no-content.component';

// import {MaterialModule} from '@angular/material';
import {BlocksService} from "./blocks/blocks.service";
import {ModalSaveComponent} from "./components/editor/modals/modalSave.component";
import {ModalSaveAsComponent} from "./components/editor/modals/modalSaveAs.component";
import {SimpleNotificationsModule} from "angular2-notifications/src/simple-notifications.module";
import {HomePage} from "./pages/HomePage";
import {InterfaceListPage} from "./pages/InterfaceListPage";
import {ListComponent} from "./components/list.component";

import { StoreModule } from '@ngrx/store';
import { EffectsModule } from '@ngrx/effects';
import { DBModule } from '@ngrx/db';
import { RouterStoreModule } from '@ngrx/router-store';
import { StoreDevtoolsModule } from '@ngrx/store-devtools';

import {reducer} from "./reducers";
import {ProgramListPage} from "./pages/ProgramListPage";
import {VersionListPage} from "./pages/VersionListPage";
import {EditorPage} from "./pages/EditorPage";
import {FetchService} from "./services/fetch.service";
import {stateService} from "./services/state.service";
import {xmlGenerator} from "./services/xmlGenerator.service";
import {ExecutionListPage} from "./pages/ExecutionListPage";
import {ReadonlyEditorPage} from "./pages/ReadonlyEditorPage";
import {BlocklyReadOnlyComponent} from "./components/blockly/blocklyReadOnly.component";
import {HelpCardComponent} from "./components/helpcard.component";
import {PostService} from "./services/post.service";
import {ModalComponent} from "./components/modal.component";



// Application wide providers
const APP_PROVIDERS = [
  ...APP_RESOLVER_PROVIDERS,
  AppState,

  BlocksService,
  RestService,
  FetchService,
  PostService,
  stateService,
  xmlGenerator
];

type StoreType = {
  state: InternalStateType,
  restoreInputValues: () => void,
  disposeOldHosts: () => void
};

/**
 * `AppModule` is the main entry point into Angular2's bootstraping process
 */
@NgModule({
  bootstrap: [ App ],
  declarations: [
    App,
    NoContentComponent,
    BlocklyComponent,
    BlocklyReadOnlyComponent,
    BreadcrumbComponent,
    ModalSaveComponent,
    ModalSaveAsComponent,
    ModalComponent,
    HelpCardComponent,

    HomePage,
    InterfaceListPage,
    ProgramListPage,
    VersionListPage,
    EditorPage,
    ReadonlyEditorPage,
    ExecutionListPage,
    ListComponent
  ],
  imports: [ // import Angular's modules
    BrowserModule,
    FormsModule,
    HttpModule,
    RouterModule.forRoot(ROUTES, { useHash: true }),
    SimpleNotificationsModule,

    StoreModule.provideStore(reducer),
    StoreDevtoolsModule.instrumentOnlyWithExtension(),
    RouterStoreModule.connectRouter()
    // MaterialModule.forRoot()
  ],
  providers: [ // expose our Services and Providers into Angular's dependency injection
    ENV_PROVIDERS,
    APP_PROVIDERS
  ]
})
export class AppModule {
  constructor(public appRef: ApplicationRef, public appState: AppState) {}

  hmrOnInit(store: StoreType) {
    if (!store || !store.state) return;
    console.log('HMR store', JSON.stringify(store, null, 2));
    // set state
    this.appState._state = store.state;
    // set input values
    if ('restoreInputValues' in store) {
      let restoreInputValues = store.restoreInputValues;
      setTimeout(restoreInputValues);
    }

    this.appRef.tick();
    delete store.state;
    delete store.restoreInputValues;
  }

  hmrOnDestroy(store: StoreType) {
    const cmpLocation = this.appRef.components.map(cmp => cmp.location.nativeElement);
    // save state
    const state = this.appState._state;
    store.state = state;
    // recreate root elements
    store.disposeOldHosts = createNewHosts(cmpLocation);
    // save input values
    store.restoreInputValues  = createInputTransfer();
    // remove styles
    removeNgStyles();
  }

  hmrAfterDestroy(store: StoreType) {
    // display new elements
    store.disposeOldHosts();
    delete store.disposeOldHosts;
  }

}

