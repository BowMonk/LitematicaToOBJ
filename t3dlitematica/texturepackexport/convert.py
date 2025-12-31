import json
import os
import shutil
from pathlib import Path

class convert_texturepack:

    def __init__(self, path: str | Path , output: str):
        if not isinstance(path, Path):
            path = Path(path)
        self.path = path
        self.tempfolder = None
        if path.suffix == ".zip":
            import zipfile
            import tempfile
            self.tempfolder = tempfile.mkdtemp()
            with zipfile.ZipFile(path, "r") as z:
                z.extractall(self.tempfolder)
            self.path = self.tempfolder
        if "assets" not in os.listdir(self.path):
            self.path = os.path.join(self.path, os.listdir(self.path)[0])
            if "assets" not in os.listdir(self.path):
                raise FileNotFoundError("找不到assets資料夾")
        self.mainpath = os.path.join(self.path, "assets", "minecraft")
        self.output = output
        os.makedirs(self.output, exist_ok=True)
        self.noneedfind = ["armor_trims","mob_effects","shield_patterns","particles"]
        self.blocksdata = {"models":{}}
        self.start()
        if self.tempfolder:
            shutil.rmtree(self.tempfolder)


    def start(self) -> None:
        sources = []
        for i in os.listdir(os.path.join(self.mainpath, "atlases")):
            if i.split(".")[0] in self.noneedfind:
                continue
            with open(os.path.join(self.mainpath, "atlases", i), "r", encoding="utf8") as f:
                blocksdata = json.load(f)
            for j in blocksdata["sources"]:
                if j["type"] == "paletted_permutations":
                    continue
                sources.append(j)
        for i in os.listdir(os.path.join(self.mainpath[:-9]+"conquest", "blockstates")):
            if i.split(".")[0] in self.noneedfind:
                continue
            with open(os.path.join(self.mainpath[:-9]+"conquest", "blockstates", i), "r", encoding="utf8") as f:
                blocksdata = json.load(f)
            for j in blocksdata["variants"]:
                if j["type"] == "paletted_permutations":
                    continue
                sources.append(j)
        needcopy = set()
        for i in sources:
            print(i)
            if i['type'] == "directory":
                needcopy.add(i["source"].split("/")[0])
            elif i['type'] == "single":
                needcopy.add(i["resource"].split("/")[0])
            elif i.get('type','default') is 'default':
                for j in i:
                    first_string = j['model'].split("/")[0]
                    if 'block' in first_string:
                        second_string = first_string[9]
                        print("we are at needcopy " + j['model'].split("/")[0])
                    needcopy.add(j['model'].split("/")[0])

        def load_model(path:str) -> None:
            if os.path.isfile(os.path.join(self.mainpath, "models", path)):
                with open(os.path.join(self.mainpath, "models", path), "r", encoding="utf8") as f:
                    blockmodel = f.read()
                    tempload = json.loads(blockmodel)
                blockmodel = blockmodel.replace("minecraft:", "")
                blockmodel:dict = json.loads(blockmodel)
                if "parent" in blockmodel and blockmodel["parent"]  not in self.blocksdata["models"]:
                    load_model(tempload["parent"].split(":")[-1]+".json")
                # 強制複寫無法解決問題的UV
                if path not in self.blocksdata["models"]:
                    if path.split("/")[-1].split(".")[0] == "sculk_sensor":
                        blockmodel["elements"][0]["faces"]["north"]["uv"] = [0, 0, 16, 8]
                        blockmodel["elements"][0]["faces"]["east"]["uv"] = [0, 0, 16, 8]
                        blockmodel["elements"][0]["faces"]["south"]["uv"] = [0, 0, 16, 8]
                        blockmodel["elements"][0]["faces"]["west"]["uv"] = [0, 0, 16, 8]
                    self.blocksdata["models"][path.split("/")[-1].split(".")[0]] = blockmodel
            if os.path.isfile(os.path.join(self.mainpath[:-9]+"conquest", "models", path)):
                with open(os.path.join(self.mainpath[:-9]+"conquest", "models", path), "r", encoding="utf8") as f:
                    blockmodel = f.read()
                    print(os.path.join(self.mainpath[:-9]+"conquest", "models", path))
                    tempload = json.loads(blockmodel)
                blockmodel = blockmodel.replace("minecraft:", "")
                blockmodel:dict = json.loads(blockmodel)
                if "parent" in blockmodel and blockmodel["parent"]  not in self.blocksdata["models"]:
                    load_model(tempload["parent"].split(":")[-1]+".json")
                # 強制複寫無法解決問題的UV
                if path not in self.blocksdata["models"]:
                    if path.split("/")[-1].split(".")[0] == "sculk_sensor":
                        blockmodel["elements"][0]["faces"]["north"]["uv"] = [0, 0, 16, 8]
                        blockmodel["elements"][0]["faces"]["east"]["uv"] = [0, 0, 16, 8]
                        blockmodel["elements"][0]["faces"]["south"]["uv"] = [0, 0, 16, 8]
                        blockmodel["elements"][0]["faces"]["west"]["uv"] = [0, 0, 16, 8]
                    self.blocksdata["models"][path.split("/")[-1].split(".")[0]] = blockmodel
        print(" We are loading models ", self.mainpath)
        for i in os.listdir(os.path.join(self.mainpath, "blockstates")):
            with open(os.path.join(self.mainpath, "blockstates", i), "r", encoding="utf8") as f:
                blockstates = json.load(f)
            if "variants" in blockstates:
                for variants in blockstates["variants"]:
                    if isinstance(blockstates["variants"][variants] , dict):
                        load_model(blockstates["variants"][variants]["model"].split(":")[-1]+".json")
                        blockstates["variants"][variants]["model"] = blockstates["variants"][variants]["model"].split("/")[-1]
                    elif isinstance(blockstates["variants"][variants] , list):
                        for j in blockstates["variants"][variants]:
                            load_model(j["model"].split(":")[-1]+".json")
                            j["model"] = j["model"].split("/")[-1]
            if "multipart" in blockstates:
                for multipart in blockstates["multipart"]:
                    if isinstance(multipart["apply"], dict):
                        load_model(multipart["apply"]["model"].split(":")[-1]+".json")
                        multipart["apply"]["model"] = multipart["apply"]["model"].split("/")[-1]
                    elif isinstance(multipart["apply"], list):
                        for j in multipart["apply"]:
                            load_model(j["model"].split(":")[-1]+".json")
                            j["model"] = j["model"].split("/")[-1]

            self.blocksdata[i.split(".")[0]] = blockstates
        for i in os.listdir(os.path.join(self.mainpath[:-9]+"conquest", "blockstates")):
            with open(os.path.join(self.mainpath[:-9]+"conquest", "blockstates", i), "r", encoding="utf8") as f:
                blockstates = json.load(f)
            if "variants" in blockstates:
                for variants in blockstates["variants"]:
                    if isinstance(blockstates["variants"][variants] , dict):
                        load_model(blockstates["variants"][variants]["model"].split(":")[-1]+".json")
                        blockstates["variants"][variants]["model"] = blockstates["variants"][variants]["model"].split("/")[-1]
                    elif isinstance(blockstates["variants"][variants] , list):
                        for j in blockstates["variants"][variants]:
                            load_model(j["model"].split(":")[-1]+".json")
                            j["model"] = j["model"].split("/")[-1]
            if "multipart" in blockstates:
                for multipart in blockstates["multipart"]:
                    if isinstance(multipart["apply"], dict):
                        load_model(multipart["apply"]["model"].split(":")[-1]+".json")
                        multipart["apply"]["model"] = multipart["apply"]["model"].split("/")[-1]
                    elif isinstance(multipart["apply"], list):
                        for j in multipart["apply"]:
                            load_model(j["model"].split(":")[-1]+".json")
                            j["model"] = j["model"].split("/")[-1]

            self.blocksdata[i.split(".")[0]] = blockstates
        with open(os.path.join(self.output, "output.json"), "w", encoding="utf8") as f:
            json.dump(self.blocksdata, f, indent=4, ensure_ascii=False)

        if os.path.exists(os.path.join(self.output,"textures")):
            shutil.rmtree(os.path.join(self.output,"textures"))
        for i in needcopy:
            new_path = ""
            print(i, self.mainpath)
            if "conquest" in i:
                new_path = self.mainpath[:-9]+"conquest"
                i = i[9:]
            else:
                new_path = self.mainpath
            shutil.copytree(os.path.join(new_path, "textures", i), os.path.join(self.output, "textures", i))





if __name__ == "__main__":
    convert_texturepack(r"C:\Users\phill\OneDrive\桌面\codetool\VanillaDefault+1.20", r"C:\Users\phill\OneDrive\Documents\coed_thing\3Dlitematica\temp")
