# embedding_search_engine

本项目包含文本语义查询、以图搜图服务，主要使用fastapi搭建服务框架，使用预训练的模型进行特征提取，使用milvus进行特征向量相似度搜索。



## reverse_image_search

以图搜图服务，实现了查询、存储数据等接口，使用towhee框架里的模型进行特征提取。

> towhee是一个开源的embedding框架，包含丰富的数据处理算法与神经网络模型，通过 Towhee，能够轻松地处理非结构化数据（如图片、视频、音频、长文本等），完成原始数据到向量的转换。
>
> milvus是一个开源矢量数据库，支持数千万个条目中的最近邻嵌入搜索。

### 整体架构

![以图搜图架构图](https://raw.githubusercontent.com/OverCookkk/PicBed/master/blogImg/%E4%BB%A5%E5%9B%BE%E6%90%9C%E5%9B%BE%E6%9E%B6%E6%9E%84%E5%9B%BE.png)

蓝线为导入数据过程，绿线为搜索过程

导入数据步骤：

1、先把每张图片数据通过resnet50生成embedding特征向量，以[embedding]的数据形式存进milvus中，milvus返回主键自增milvus_id。

2、对milvus中的embedding数据建立索引，然后将milvus_id和对应的图像路径存储进mysql中。



搜索步骤：

1、当执行搜索的时候，resnet50会将搜索的文本转换成embedding特征向量，输入milvus中进行特征相似度查询，并返回topk个相似结果（返回id等信息），通过id字段去mysql中查询到对应的图像数据。



## text_semantic_search

文本语义搜索服务，实现了查询、存储数据的接口。

bert是Google开源的一个通用的语言表示模型，milvus是一个特向向量相似度搜索引擎，towhee是一个开源的embedding框架，包含丰富的数据处理算法与神经网络模型，通过 Towhee，能够轻松地处理非结构化数据（如图片、视频、音频、长文本等），完成原始数据到向量的转换。本项目将milvus、bert模型以及向量引擎框架towhee相结合，简单搭建文本语义搜索服务。

### 整体架构

![文本语义搜索服务流程图](https://raw.githubusercontent.com/OverCookkk/PicBed/master/github_projects_images/文本语义搜索服务流程图.png)

蓝线为导入数据过程，绿线为搜索过程

导入数据步骤：

1、先把每条文本数据通过bert模型生成对应728维的embedding特征向量，然后对每个文本数据设置一个唯一的id，以[id, embedding]的数据形式存进milvus中。

2、对milvus中的embedding数据建立索引，然后将id和对应的文本数据存储进mysql中。



搜索步骤：

1、当执行搜索的时候，bert会将搜索的文本转换成embedding特征向量，输入milvus中进行特征相似度查询，并返回topk个相似结果（返回id等信息），通过id字段去mysql中查询到对应的文本数据。





### 启动过程

1、创建虚拟环境后，执行`pip install -r requirements.txt`。

2、在`config.py`和`run.py`中填好milvus和mysql的配置后，执行`python run.py`启动服务。

3、`test_main.py`为测试代码，导入的文本文件格式为csv，包含`title`和`text`两个字段。



## text_image_search

以文搜图指的是，根据文本描述，从图像数据库中检索与文本内容相似的图像数据并返回。

文本与图像使用预训练好的中文版本的[Chinese-CLIP](https://github.com/OFA-Sys/Chinese-CLIP#checkpointing)模型来进行特征提取，

> CLIP是OpenAI在2021年提出的多模态神经网络模型，该模型基于OpenAI 收集到的 4 亿对图像文本对进行训练，分别将文本和图像进行编码，之后使用 metric learning 进行权重，其目标是将图像与文本的相似性提高。



### 整体架构

![以文搜图服务流程图](https://raw.githubusercontent.com/OverCookkk/PicBed/master/blogImg/%E4%BB%A5%E6%96%87%E6%90%9C%E5%9B%BE%E6%9C%8D%E5%8A%A1%E6%B5%81%E7%A8%8B%E5%9B%BE.png)

蓝线为导入数据过程，绿线为搜索过程

导入数据步骤：

1、先把图片url等图片信息存入mysql，返回图片在数据库中的主键id；

2、图片经过clip模型得到embedding信息，再把图片的主键id和它的embedding存入milvus中。



搜索步骤：

1、输入文本信息经过clip模型得到对应的embedding，embedding输入milvus进行相似度查询，搜索到top k个图片，包含图片id，再通过图片id去mysql中查找到完整的图片信息。



### 微调clip模型

- [ ] TODO
