# AsiaCCS25-ProbeShooter
This repository contains the artifacts and source code for the paper titled 
_**"PʀᴏʙᴇSʜᴏᴏᴛᴇʀ: A New Practical Approach for Probe Aiming"**_ to be presented at _**ASIA CCS '25**_. 
The preprint of the paper is available [here](https://eprint.iacr.org/2025/20).

## Structure
```
.
├── Dockerfile
├── LICENSE
├── PSD-chunks
│   ├── PSA-IMXRT1061-24mhz
│   │   ├── freq.npy
│   │   ├── meta.txt
│   │   └── psd_chunk.npy
│   ├── PSA-RPI4-multi-core-each-1200mhz
│   │   ├── core0
│   │   │   ├── freq.npy
│   │   │   ├── meta.txt
│   │   │   └── psd_chunk.npy
│   │   ├── core1
│   │   │   ├── freq.npy
│   │   │   ├── meta.txt
│   │   │   └── psd_chunk.npy
│   │   ├── core2
│   │   │   ├── freq.npy
│   │   │   ├── meta.txt
│   │   │   └── psd_chunk.npy
│   │   └── core3
│   │       ├── freq.npy
│   │       ├── meta.txt
│   │       └── psd_chunk.npy
│   ├── PSP-IMXRT1061-24mhz
│   │   ├── freq.npy
│   │   ├── meta.txt
│   │   └── psd_chunk.npy
│   ├── PSP-RPI4-dynamic-frequency
│   │   ├── freq.npy
│   │   ├── meta.txt
│   │   ├── psd_chunk.npy
│   │   └── real_freq.npy
│   └── PSP-RPI4-multi-core-1200mhz
│       ├── freq.npy
│       ├── meta.txt
│       └── psd_chunk.npy
├── README.md
├── docker-compose.yml
├── gadget
│   ├── bcm2711
│   │   ├── aes-128-inf
│   │   │   ├── aes.c
│   │   │   ├── aes.h
│   │   │   ├── build.sh
│   │   │   └── main.c
│   │   ├── measuring
│   │   │   ├── init
│   │   │   │   ├── Makefile
│   │   │   │   ├── enable_ccr.c
│   │   │   │   └── enable_ccr.mod.c
│   │   │   └── measuring-gadget
│   │   │       ├── build.sh
│   │   │       ├── main.c
│   │   │       └── main_original.c
│   │   ├── udiv-11c
│   │   │   ├── build.sh
│   │   │   └── main.c
│   │   ├── udiv-13c
│   │   │   ├── build.sh
│   │   │   └── main.c
│   │   ├── udiv-17c
│   │   │   ├── build.sh
│   │   │   └── main.c
│   │   └── udiv-7c
│   │       ├── build.sh
│   │       └── main.c
│   └── imxrt1061
│       └── pushpop-7c.zip
├── pyproject.toml
├── scripts
│   ├── generate_figure1.py
│   ├── generate_figure11.py
│   ├── generate_figure12.py
│   ├── generate_figure2.py
│   ├── generate_figure20a.py
│   └── psd_chunk_acquisition.py
└── source
    ├── dummy_hardware_api
    │   ├── DummySpectrumAnalyzer.py
    │   ├── DummyXYZ.py
    │   └── __init__.py
    └── probeshooter
        ├── __init__.py
        ├── aiming
        │   ├── __init__.py
        │   ├── aiming.py
        │   ├── coord_converter.py
        │   ├── filter.py
        │   └── finder.py
        ├── handler
        │   ├── __init__.py
        │   ├── psd_chunk_dtype.py
        │   └── psd_chunk_handler.py
        └── plotter
            ├── __init__.py
            └── map.py
```
> [!IMPORTANT]
> We only provide **dummy classes** for hardware control. 
> To perform the _**PSD Chunk Acquisition**_ step, you need to implement the control logic to operate your own equipment.

## Getting Started with Docker

### ❶. Pull a pre-built image from Docker Hub
We have pre-built and uploaded the files and data of this repository as a Docker image to Docker Hub.
By running the following command, you can pull and run the Docker image.
For more details, you can check [here](https://hub.docker.com/r/daehyeonbae/asiaccs25-probeshooter).

`$ docker run -it daehyeonbae/asiaccs25-probeshooter:250812`

> [!NOTE]
> Due to GitHub's storage limitations, the PSD chunks are included only in the Docker image. 

### ❷. Run scripts
Once you run the container, you will have access to a Bash shell. 
Then, by executing the scripts inside `AsiaCCS25-ProbeShooter/scripts`, 
the corresponding result figures will be generated and saved in `AsiaCCS25-ProbeShooter/scripts/output`.

## Citation

#### MLA
> Bae, Daehyeon, et al. "ProbeShooter: A New Practical Approach for Probe Aiming." _Proceedings of the 20th ACM Asia Conference on Computer and Communications Security (ASIA CCS)_. 2025.

#### APA
> Bae, D., Park, S., Choi, M., Jung, Y., Jeong, C., Kim, H., & Hong, S. (2025, August). ProbeShooter: A New Practical Approach for Probe Aiming. In _Proceedings of the 19th ACM Asia Conference on Computer and Communications Security (ASIA CCS)_.

#### ISO 690
> BAE, Daehyeon, et al. ProbeShooter: A New Practical Approach for Probe Aiming. In: _Proceedings of the 20th ACM Asia Conference on Computer and Communications Security (ASIA CCS)_. 2025.

#### IEEE
> D. Bae, S. Park, M. Choi, Y.-G. Jung, C. Jeong, H. Kim, and S. Hong, "ProbeShooter: A new practical approach for probe aiming," in _Proc. 20th ACM Asia Conf. Comput. Commun. Secur. (ASIA CCS)_, 2025.

#### BibTeX
```
@inproceedings{Bae2025ProbeShooter,
    author = {Daehyeon Bae and Sujin Park and Minsig Choi and Young-Giu Jung and Changmin Jeong and Heeseok Kim and Seokhie Hong},
    title = {{ProbeShooter}: A New Practical Approach for Probe Aiming},
    booktitle = {Proceedings of the 20th ACM Asia Conference on Computer and Communications Security (ASIA CCS)},
    year = {2025},
    address = {Hanoi, Vietnam},
    doi = {10.1145/3708821.3710815},
    isbn = {9798400714108}
}
```

## Contact
- Daehyeon Bae ([dh_bae [at] korea.ac.kr](mailto:dh_bae@korea.ac.kr) / [@noeyheadb](https://github.com/noeyheadb))
