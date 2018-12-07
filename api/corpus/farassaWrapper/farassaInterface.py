import inspect

import jpype
from jpype import *
import os

class Farasa:
    def __init__(self):
        jvmPath = jpype.getDefaultJVMPath()
        root = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
        root += "/libs/jars/"
        path_to_jars = str.join(":", [root + name for name in os.listdir(root)])
        # if not jpype.isJVMStarted():
        if not jpype.isJVMStarted():
            jpype.startJVM(jvmPath,
                       "-Djava.class.path="+path_to_jars)
        self.far = JPackage("com").qcri.farasa.segmenter.Farasa()

    def segment(self,text):
        return self.far.segmentLine(text)

    def lemmatize(self, text):
        return self.far.lemmatizeLine(text)
    #
    def tag(self,text):
        Farasa = JPackage("com").qcri.farasa.segmenter.Farasa
        FarPosTagger = JPackage("com").qcri.farasa.pos.FarasaPOSTagger
        far = Farasa()
        tagger = FarPosTagger(far)
        lines = self.segment(text)
        sents = tagger.tagLine(lines)

        tab = [(w.surface,w.guessPOS,w.genderNumber)for w in sents.clitics]
        # print (tab)
        return tab
        # print(sents)

if __name__ == "__main__":
    test = "يُشار إلى أن اللغة العربية يتحدثها أكثر من 422 مليون نسمة ويتوزع متحدثوها في المنطقة المعروفة باسم الوطن العربي بالإضافة إلى العديد من المناطق الأخرى المجاورة مثل الأهواز وتركيا وتشاد والسنغال وإريتريا وغيرها. وهي اللغة الرابعة من لغات منظمة الأمم المتحدة الرسمية الست."
    far = Farasa()
    res = far.lemmatize(test)
    print(res)