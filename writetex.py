#!/usr/bin/env python
# -*- coding:utf-8
"""
writetex.py
An Latex equation editor for Inkscape.

:Author: WANG Longqi <iqgnol@gmail.com>
:Date: 2015-06-14
:Version: v0.4

This file is a part of WriteTeX extension for Inkscape. For more information,
please refer to http://wanglongqi.github.io/WriteTeX.
"""

import inkex,os,tempfile,sys,copy
WriteTexNS=u'http://wanglongqi.github.io/WriteTeX'
# from textext
SVG_NS=u"http://www.w3.org/2000/svg"
XLINK_NS = u"http://www.w3.org/1999/xlink"

class WriteTex(inkex.Effect):
    def __init__(self):
        inkex.Effect.__init__(self)
        self.OptionParser.add_option("-f","--formula",
                        action="store",type="string",
                        dest="formula",default="",
                        help="LaTeX formula")
        self.OptionParser.add_option("-p","--preamble",
                        action="store",type="string",
                        dest="preamble",default="",
                        help="Preamble File")
        self.OptionParser.add_option("--read-as-line",
                        action="store",type="string",
                        dest="preline",default="",
                        help="Read preamble as string")
        self.OptionParser.add_option("-s","--scale",
                        action="store",type="string",
                        dest="scale",default="",
                        help="Scale Factor")
        self.OptionParser.add_option("-i","--inputfile",
                        action="store",type="string",
                        dest="inputfile",default="",
                        help="Read From File")
        self.OptionParser.add_option("--action",action="store",
                        type="string",dest="action",
                        default=None,help="")
        self.OptionParser.add_option("-r","--rescale",
                        action="store",type="string",
                        dest="rescale",default="",
                        help="Rescale the object")
    def effect(self):
        self.options.scale=float(self.options.scale)
        action=self.options.action.strip("\"")
        if action=="viewold":
            for i in self.options.ids:
                node=self.selected[i]
                if node.tag != '{%s}g' % SVG_NS: continue                
                if '{%s}text'%WriteTexNS in node.attrib:
                    print >>sys.stderr,node.attrib.get('{%s}text'%WriteTexNS,'').decode('string-escape')
                    return
            print >>sys.stderr,"No text find."  
            return
        else:
            if action == "new":
                self.text=self.options.formula
            else:
                f=open(self.options.inputfile)
                self.text=f.read()
                f.close()

            if self.text == "":
                print >>sys.stderr,"empty LaTeX input. Nothing is changed."
                return
                
            tmp_dir=tempfile.mkdtemp("","writetex-");
            tex_file="writetex.tex"
            svg_file="writetex.svg"
            pdf_file="writetex.pdf"
            log_file="writetex.log"

            if self.options.preline == "true":
                preamble = self.options.preamble
            else:
                if self.options.preamble=="":
                    preamble=""
                else:
                    f=open(self.options.preamble)
                    preamble=f.read()
                    f.close()
                
            self.tex=r"""
            \usemodule[zhfonts]
            %s
            \startTEXpage
            %s
            \stopTEXpage

            """ % (preamble,self.text) 
            
            os.chdir(tmp_dir)
            
            tex=open(tex_file,'w')
            tex.write(self.tex)
            tex.close()
            
            os.popen("ctx --once --jit --purgeall %s" % (tex_file))
            if not os.path.exists(pdf_file):
                print >>sys.stderr, "Latex error: check your latex file and preamble."
                print >>sys.stderr,open(log_file).read()
            else:
                    os.popen('pdf2svg %s %s'%(pdf_file,svg_file))
                    self.merge_pdf2svg_svg(svg_file)
            
            os.chdir("/tmp")
            os.popen("rm -rf %s" % (tmp_dir))


    def merge_pdf2svg_svg(self,svg_file):
        def svg_to_group(self,svgin):  
            target={}
            for node in svgin.xpath('//*[@id]'):
                target['#'+node.attrib['id']]=node
                
            for node in svgin.xpath('//*'):
                if node.attrib.has_key('{%s}href'%XLINK_NS):
                    href=node.attrib['{%s}href'%XLINK_NS]
                    p=node.getparent()
                    p.remove(node)
                    trans='translate(%s,%s)'%(node.attrib['x'],node.attrib['y'])
                    for i in target[href].iterchildren():
                        i.attrib['transform']=trans
                        p.append(copy.copy(i))

            svgout = inkex.etree.Element(inkex.addNS('g','WriteTexNS'))
            for node in svgin:
                if node is svgout: continue
                if node.tag == '{%s}defs' % SVG_NS:
                    continue
                svgout.append(node)
            return svgout
                    
        doc=inkex.etree.parse(svg_file)
        svg=doc.getroot()
        newnode=svg_to_group(self,svg)
        newnode.attrib['{%s}text'%WriteTexNS]=self.text.encode('string-escape')
        
        replace=False
            
        for i in self.options.ids:
            node=self.selected[i]
            if node.tag != '{%s}g' % SVG_NS: continue            
            if '{%s}text'%WriteTexNS in node.attrib:
                replace=True
                break
                
        if replace:
            try:
                if self.options.rescale=='true':
                    newnode.attrib['transform']='matrix(%f,0,0,%f,%f,%f)' %(self.options.scale,self.options.scale,
                                                                            self.options.scale,-50*self.options.scale)
                else:
                    if node.attrib.has_key('transform'):
                        newnode.attrib['transform']=node.attrib['transform']
                    else:
                        newnode.attrib['transform']='matrix(%f,0,0,%f,%f,%f)' %(self.options.scale,self.options.scale,
                                                                                self.options.scale,-50*self.options.scale)
                newnode.attrib['style']=node.attrib['style']  
            except:
                pass
            p=node.getparent()
            p.remove(node)
            p.append(newnode)
        else:
            self.current_layer.append(newnode)
            newnode.attrib['transform']='matrix(%f,0,0,%f,%f,%f)' %(self.options.scale,self.options.scale,
                                                                    self.options.scale,-50*self.options.scale)

                   
if __name__ == '__main__':
    e=WriteTex()
    e.affect()
