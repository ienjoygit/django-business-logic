import { Injectable } from '@angular/core';

import { RestService } from './rest.service';


import { ProgramInterface, ProgramInterfaceCollection } from "../models/programInterface";
import { Program, ProgramCollection } from "../models/program";
import { Version, VersionCollection } from "../models/version";
import {Observable} from "rxjs";

@Injectable()
export class BaseService {
  protected baseUrl = '/business-logic/rest';

  programInterfaces: any;
  programs: any;
  versions: any;

  constructor(private rest: RestService){

  }

  fetchProgramInterfaces(){

    this.programInterfaces = new ProgramInterfaceCollection();
    return this.rest.get(this.programInterfaces.getUrl()).map((data) => {
      data.results.map( (result) => {
        this.programInterfaces.addNew( new ProgramInterface(result["id"], result["title"]) );
      } );
    });
  }

  fetchPrograms( interfaceID: number ){
    if(!this.programInterfaces){
      return this.fetchProgramInterfaces().flatMap(() => {
        return this.fetchPrograms(interfaceID);
      });
    }

    this.programInterfaces.setCurrent(this.programInterfaces.getModelByID( interfaceID ));

    this.programs = new ProgramCollection();

    return this.rest.getWithSearchParams(
      this.programs.getUrl(),
      [ ['program_interface',  interfaceID] ]
    ).map((data) => {
      data.results.map( (result) => {
        this.programs.addNew( new Program(result["id"], result["title"]) );
      } );
    });
  }

  fetchVersions( interfaceID: number, programID: number  ){
    if(!this.programs){
      return this.fetchProgramInterfaces().flatMap(() => {
        return this.fetchPrograms(interfaceID).flatMap(() => {
          return this.fetchVersions(interfaceID, programID);
        });
      });
    }

    this.programInterfaces.setCurrent(this.programInterfaces.getModelByID( interfaceID ));
    this.programs.setCurrent(this.programs.getModelByID( programID ));

    this.versions = new VersionCollection();

    return this.rest.getWithSearchParams(
      this.versions.getUrl(),
      [ [ 'program',  this.programs.getCurrent().getID()] ]
    ).map((data) => {
      data.results.map( (result) => {
        this.versions.addNew( new Version(result["id"], result["title"]) );
      } );
    });
  }


}
