# Install the SDK
FROM vnmd/clearswi_1.0.0:20211018 AS clearswi

FROM vnmd/qsmxt_1.1.7:latest

WORKDIR /root

RUN apt-get update -y && \
    apt-get install -y python3 python3-pip wget && \
    rm -rf /var/lib/apt/lists/*

RUN pip3 install qmenta-sdk-lib
RUN python3 -m qmenta.sdk.make_entrypoint /root/entrypoint.sh /root/

# Install your software requirements and run other config commands (may take several minutes)
RUN apt-get update -y && \
    apt-get install -y mrtrix libfreetype6-dev libxft-dev wkhtmltopdf xvfb && \
    rm -rf /var/lib/apt/lists/* && \
    pip3 install matplotlib numpy pdfkit tornado

# A virtual x framebuffer is required to generate PDF files with pdfkit
RUN echo '#!/bin/bash\nxvfb-run -a --server-args="-screen 0, 1024x768x24" /usr/bin/wkhtmltopdf -q $*' > /usr/bin/wkhtmltopdf.sh && \
    chmod a+x /usr/bin/wkhtmltopdf.sh && \
    ln -s /usr/bin/wkhtmltopdf.sh /usr/local/bin/wkhtmltopdf

# Copy clearswi files from clearswi container
COPY --from=clearswi /opt/install_packages.jl ./

RUN julia install_packages.jl

# Setup image to run on cloud platforms
COPY v0/run.py clearswi.jl /root/
ENV FLYWHEEL=/flywheel/v0
RUN mkdir -p ${FLYWHEEL}
COPY v0/run.py ${FLYWHEEL}/run.py

RUN mkdir /root/clearswi_output