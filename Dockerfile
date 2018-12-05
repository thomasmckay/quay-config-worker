FROM registry.redhat.io/rhel7:7.6
#FROM centos:7

ENV PYTHON_VERSION=2.7 \
    PATH=$HOME/.local/bin/:$PATH \
    PYTHONUNBUFFERED=1 \
    PYTHONIOENCODING=UTF-8 \
    LC_ALL=en_US.UTF-8 \
    LANG=en_US.UTF-8 \
    PIP_NO_CACHE_DIR=off

ENV WORKER_DIR /ansible-worker
RUN mkdir $WORKER_DIR
WORKDIR $WORKER_DIR

RUN INSTALL_PKGS="python27 python27-python-pip" && \
    UNINSTALL_PKGS="python27-python-pip gcc-c++ git" && \
    yum install -y yum-utils && \
    yum-config-manager --quiet --disable "*" >/dev/null && \
    yum-config-manager --quiet --enable rhel-7-server-rpms rhel-server-rhscl-7-rpms --save >/dev/null && \
    yum -y --setopt=tsflags=nodocs install $INSTALL_PKGS $UNINSTALL_PKGS && \
    yum -y clean all --enablerepo='*'

COPY . .

RUN scl enable python27 "pip install --upgrade pip && pip install -r requirements.txt --no-cache"

RUN UNINSTALL_PKGS="python27-python-pip gcc-c++ git" && \
    yum remove -y $UNINSTALL_PKGS && \
    yum clean all

EXPOSE 8688
EXPOSE 8788

CMD scl enable python27 "./ansible_worker.sh"