import { BaseCollection } from "./base.collection";
import { BaseModel } from "./base.model";
import {Environment} from "./environment";

export class Version extends BaseModel{
  environment: Environment;
  xml: string;

  description: string;

  constructor(id: number, title: string, description: string){
    super(id, title);
    this.description = description;
    this.url = `/program-version/${this.id}`;
  }

  getDescription(){
    return this.description;
  }

  getEnvironment(){
    return this.environment;
  }

  setEnvironment(data: any){
    this.environment = new Environment(data);
  }

  setXml(xml: string){
    this.xml = xml;
  }
}

export class VersionCollection extends BaseCollection{
  constructor(){
    super('/program-version');
  }

  static getBaseURL(){
    return '/business-logic/rest/program-version'
  }
}
