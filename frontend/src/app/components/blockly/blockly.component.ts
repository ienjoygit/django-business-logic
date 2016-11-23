import {
  Component,
  Input,
  ViewChild,
} from '@angular/core';

@Component({
  selector: 'blockly',
  template: `
    <div #blocklyArea></div>   
    <div #blocklyDiv [ngStyle]="style"></div>
    `,
  providers: []
})

export class BlocklyComponent {

  @Input() version: any;
  @Input() xmlForReferenceDescriptors: any;
  @Input() xmlForArgumentFields: any;
  @Input() xmlForFunctionLibs: any;

  @ViewChild('blocklyDiv') blocklyDiv;
  @ViewChild('blocklyArea') blocklyArea;

  style = {
    width: '100%',
    height: '90%',
    position: 'absolute'
  };

  private workspace: Blockly.Workspace;

  constructor(){

  }


  ngAfterViewInit() {

  }

  createWorkspace(){

      let toolbox = `<xml>
                        ${require('./blockly-toolset.html')}
                        ${this.xmlForReferenceDescriptors}
                        ${this.xmlForArgumentFields}
                        ${this.xmlForFunctionLibs}
                     </xml>`;
      this.workspace = Blockly.inject(this.blocklyDiv.nativeElement,
        {
          toolbox: toolbox,
          trashcan: true,
          sounds: false,
          media: "./blockly/"
        });

      this.loadVersionXml();

  }

  loadVersionXml(){
    let xml = Blockly.Xml.textToDom(this.version["xml"]);

    Blockly.Xml.domToWorkspace(xml, this.workspace);
  }


  ngOnChanges(changes: any): any {

    if(changes.version && changes.version.currentValue){

    }

    if(this.xmlForReferenceDescriptors && this.xmlForArgumentFields){
      this.createWorkspace();
    }

  }

  getXml(){
    return Blockly.Xml.domToText( Blockly.Xml.workspaceToDom(this.workspace, false) );
  }

  initXml(xmlText) {
    this.workspace.clear();
    let xml = Blockly.Xml.textToDom(xmlText);
    Blockly.Xml.domToWorkspace(xml, this.workspace);
  }
}
