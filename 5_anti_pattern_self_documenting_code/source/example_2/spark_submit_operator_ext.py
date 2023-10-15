# -*- coding: utf-8 -*-
"""
SparkSubmitOperatorExt позволяет использовать различные СПУЗы в дагах Airflow 1.
Решена проблема падения тасок из-за ошибки kerberos-аутентификации (GSS).
"""

from airflow.contrib.operators.spark_submit_operator import SparkSubmitOperator

from dlk_airflow_common.hooks.spark_submit_hook_ext import SparkSubmitHookExt
from dlk_airflow_common.library.run_as_user import update_popen_krb5ccname, default_krb5ccname_func


class SparkSubmitOperatorExt(SparkSubmitOperator):

    def __init__(self, yarn_queue=None, deploy_mode=None, driver_cores=None, archives=None, **kwargs):
        """
        :param archives:
        :param kwargs:
        """
        super().__init__(**kwargs)
        self.yarn_queue = yarn_queue
        self.deploy_mode = deploy_mode
        self.driver_cores = driver_cores
        self.archives = archives

    def execute(self, context):
        """
        Call the SparkSubmitHook to run the provided spark job
        """
        self._hook = SparkSubmitHookExt(
            yarn_queue=self.yarn_queue,
            deploy_mode=self.deploy_mode,
            archives=self.archives,
            driver_cores=self.driver_cores,
            conf=self._conf,
            conn_id=self._conn_id,
            files=self._files,
            py_files=self._py_files,
            driver_class_path=self._driver_class_path,
            jars=self._jars,
            java_class=self._java_class,
            packages=self._packages,
            exclude_packages=self._exclude_packages,
            repositories=self._repositories,
            total_executor_cores=self._total_executor_cores,
            executor_cores=self._executor_cores,
            executor_memory=self._executor_memory,
            driver_memory=self._driver_memory,
            keytab=self._keytab,
            principal=self._principal,
            name=self._name,
            num_executors=self._num_executors,
            application_args=self._application_args,
            env_vars=self._env_vars,
            verbose=self._verbose
        )
        new_popen_env_vars = update_popen_krb5ccname(self.run_as_user, krb5ccname_func=default_krb5ccname_func)
        self._hook.submit(self._application, env=new_popen_env_vars)

