'''
Samba custom metrics for port streeming
'''
import subprocess
import re
import time
from typing import List, Tuple
from prometheus_client import start_http_server, Gauge
from pydantic import BaseModel

# Define Prometheus metrics
metrics_mapping = {
    'connect_count': Gauge('smb2_connect_count', 'Number of connect count'),
    'disconnect_count': Gauge('smb2_disconnect_count', 'Number of disconnect cont'),
    'idle_count': Gauge('smb2_idle_count', 'Number of idle count'),
    'idle_time': Gauge('smb2_idle_time', 'Number of Idle time'),
    'cpu_user_time': Gauge('smb2_cpu_user_time', 'Number of cpu user time'),
    'cpu_system_time': Gauge('smb2_cpu_system_time', 'Number of system time'),
    'request_count': Gauge('smb2_request_count', 'Number of smb request count'),
    'push_sec_ctx_count': Gauge('smb2_push_sec_ctx_count', 'Number of push sec ctx count'),
    'set_sec_ctx_count': Gauge('smb2_set_sec_ctx_count', 'Number of set sec ctx count'),
    'set_root_sec_ctx_count': Gauge('smb2_set_root_sec_ctx_count', \
        'Number of set root sec ctx count'),
    'pop_sec_ctx_count': Gauge('smb2_pop_sec_ctx_count', 'Number of pop sec ctx count'),
    'syscall_opendir_count': Gauge('smb2_syscall_opendir_count', 'Count of opendir system calls'),
    'syscall_opendir_time': Gauge('smb2_syscall_opendir_time', \
        'Time spent in opendir system calls'),
    'syscall_fdopendir_count': Gauge('smb2_syscall_fdopendir_count', \
        'Count of fdopendir system calls'),
    'syscall_fdopendir_time': Gauge('smb2_syscall_fdopendir_time', \
        'Time spent in fdopendir system calls'),
    'syscall_readdir_count': Gauge('smb2_syscall_readdir_count', \
        'Count of readdir system calls'),
    'syscall_readdir_time': Gauge('smb2_syscall_readdir_time', \
        'Time spent in readdir system calls'),
    'syscall_seekdir_count': Gauge('smb2_syscall_seekdir_count', \
        'Count of seekdir system calls'),
    'syscall_seekdir_time': Gauge('smb2_syscall_seekdir_time', \
        'Time spent in seekdir system calls'),
    'syscall_telldir_count': Gauge('smb2_syscall_telldir_count', \
        'Count of telldir system calls'),
    'syscall_telldir_time': Gauge('smb2_syscall_telldir_time', \
        'Time spent in telldir system calls'),
    'syscall_rewinddir_count': Gauge('smb2_syscall_rewinddir_count', \
        'Count of rewinddir system calls'),
    'syscall_rewinddir_time': Gauge('smb2_syscall_rewinddir_time', \
        'Time spent in rewinddir system calls'),
    'syscall_mkdir_count': Gauge('smb2_syscall_mkdir_count', \
        'Count of mkdir system calls'),
    'syscall_mkdir_time': Gauge('smb2_syscall_mkdir_time', \
        'Time spent in mkdir system calls'),
    'syscall_rmdir_count': Gauge('smb2_syscall_rmdir_count', \
        'Count of rmdir system calls'),
    'syscall_rmdir_time': Gauge('smb2_syscall_rmdir_time', \
        'Time spent in rmdir system calls'),
    'syscall_closedir_count': Gauge('smb2_syscall_closedir_count', \
        'Count of closedir system calls'),
    'syscall_closedir_time': Gauge('smb2_syscall_closedir_time', \
        'Time spent in closedir system calls'),
    'syscall_open_count': Gauge('smb2_syscall_open_count', \
        'Count of open system calls'),
    'syscall_open_time': Gauge('smb2_syscall_open_time', \
        'Time spent in open system calls'),
    'syscall_createfile_count': Gauge('smb2_syscall_createfile_count', \
        'Count of createfile system calls'),
    'syscall_createfile_time': Gauge('smb2_syscall_createfile_time', \
        'Time spent in createfile system calls'),
    'syscall_close_count': Gauge('smb2_syscall_close_count', 'Count of close system calls'),
    'syscall_close_time': Gauge('smb2_syscall_close_time', 'Time spent in close system calls'),
    'syscall_pread_count': Gauge('smb2_syscall_pread_count', 'Count of pread system calls'),
    'syscall_pread_time': Gauge('smb2_syscall_pread_time', 'Time spent in pread system calls'),
    'syscall_pread_idle': Gauge('smb2_syscall_pread_idle', 'Idle time spent in pread system calls'),
    'syscall_pread_bytes': Gauge('smb2_syscall_pread_bytes', 'Bytes read in pread system calls'),
    'syscall_asys_pread_count': Gauge('smb2_syscall_asys_pread_count', \
        'Count of asynchronous pread system calls'),
    'syscall_asys_pread_time': Gauge('smb2_syscall_asys_pread_time', \
        'Time spent in asynchronous pread system calls'),
    'syscall_asys_pread_idle': Gauge('smb2_syscall_asys_pread_idle', \
        'Idle time spent in asynchronous pread system calls'),
    'syscall_asys_pread_bytes': Gauge('smb2_syscall_asys_pread_bytes', \
        'Bytes read in asynchronous pread system calls'),
    'syscall_pwrite_count': Gauge('smb2_syscall_pwrite_count', \
        'Count of pwrite system calls'),
    'syscall_pwrite_time': Gauge('smb2_syscall_pwrite_time', \
        'Count of pwrite system time'),
    'syscall_pwrite_idle': Gauge('smb2_syscall_pwrite_idle', \
        'Idle time spent in pwrite system calls'),
    'syscall_pwrite_bytes': Gauge('smb2_syscall_pwrite_bytes', \
        'Bytest wirte in pwirte system calls'),
    'syscall_asys_pwrite_count': Gauge('smb2_syscall_asys_pwrite_count', \
        'Count of asynchronous pwrite system calls'),
    'syscall_asys_pwrite_time': Gauge('smb2_syscall_asys_pwrite_time', \
        'Time spent in asynchronous pwrite system calls'),
    'syscall_asys_pwrite_idle': Gauge('smb2_syscall_asys_pwrite_idle', \
        'Idle time spent in asynchronus pwrite system calls'),
    'syscall_asys_pwrite_bytes': Gauge('smb2_syscall_asys_pwrite_bytes', \
        'Bytes write in asynchronous pwrite system calls'),
    'syscall_lseek_count': Gauge('smb2_syscall_lseek_count', 'Number of lseek system calls'),
    'syscall_lseek_time': Gauge('smb2_syscall_lseek_time', 'Time spent in lseek system calls'),
    'syscall_sendfile_count': Gauge('smb2_syscall_sendfile_count', \
        'Number of sendfile system calls'),
    'syscall_sendfile_time': Gauge('smb2_syscall_sendfile_time', \
        'Time spent in sendfile system calls'),
    'syscall_sendfile_idle': Gauge('smb2_syscall_sendfile_idle', \
        'Idle time between sendfile system calls'),
    'syscall_sendfile_bytes': Gauge('smb2_syscall_sendfile_bytes', \
        'Number of bytes sent by sendfile system calls'),
    'syscall_recvfile_count': Gauge('smb2_syscall_recvfile_count', \
        'Number of recvfile system calls'),
    'syscall_recvfile_time': Gauge('smb2_syscall_recvfile_time', \
        'Time spent in recvfile system calls'),
    'syscall_recvfile_idle': Gauge('smb2_syscall_recvfile_idle', \
        'Idle time between recvfile system calls'),
    'syscall_recvfile_bytes': Gauge('smb2_syscall_recvfile_bytes', \
        'Number of bytes received by recvfile system calls'),
    'syscall_rename_count': Gauge('smb2_syscall_rename_count', \
        'Number of rename system calls'),
    'syscall_rename_time': Gauge('smb_syscall_rename_time', \
        'Time spent in rename system calls'),
    'syscall_rename_at_count': Gauge('smb2_syscall_rename_at_count', \
        'Number of rename_at system calls'),
    'syscall_rename_at_time': Gauge('smb2_syscall_rename_at_time', \
        'Total time spent in rename_at system calls'),
    'syscall_asys_fsync_count': Gauge('smb2_syscall_asys_fsync_count', \
        'Number of asys_fsync system calls'),
    'syscall_asys_fsync_time': Gauge('smb2_syscall_asys_fsync_time', \
        'Total time spent in asys_fsync system calls'),
    'syscall_stat_count': Gauge('smb2_syscall_stat_count', \
        'Number of stat system calls'),
    'syscall_stat_time': Gauge('smb2_syscall_stat_time', \
        'Total time spent in stat system calls'),
    'syscall_fstat_count': Gauge('smb2_syscall_fstat_count', \
        'Number of fstat system calls'),
    'syscall_fstat_time': Gauge('smb2_syscall_fstat_time', \
        'Total time spent in fstat system calls'),
    'syscall_lstat_count': Gauge('smb2_syscall_lstat_count', \
        'Number of lstat system calls'),
    'syscall_lstat_time': Gauge('smb2_syscall_lstat_time', \
        'Total time spent in lstat system calls'),
    'syscall_get_alloc_size_count': Gauge('smb2_syscall_get_alloc_size_count', \
        'Number of get_alloc_size system calls'),
    'syscall_get_alloc_size_time': Gauge('smb2_syscall_get_alloc_size_time', \
        'Total time spent in get_alloc_size system calls'),
    'syscall_unlink_count': Gauge('smb2_syscall_unlink_count', 'Number of unlink system calls'),
    'syscall_unlink_time': Gauge('smb2_syscall_unlink_time', 'Time spent in unlink system calls'),
    'syscall_chmod_count': Gauge('smb2_syscall_chmod_count', 'Number of chmod system calls'),
    'syscall_chmod_time': Gauge('smb2_syscall_chmod_time', 'Time spent in chmod system calls'),
    'syscall_fchmod_count': Gauge('smb2_syscall_fchmod_count', 'Number of fchmod system calls'),
    'syscall_fchmod_time': Gauge('smb2_syscall_fchmod_time', 'Time spent in fchmod system calls'),
    'syscall_chown_count': Gauge('smb2_syscall_chown_count', 'Number of chown system calls'),
    'syscall_chown_time': Gauge('smb2_syscall_chown_time', 'Time spent in chown system calls'),
    'syscall_fchown_count': Gauge('smb2_syscall_fchown_count', 'Number of fchown system calls'),
    'syscall_fchown_time': Gauge('smb2_syscall_fchown_time', 'Time spent in fchown system calls'),
    'syscall_lchown_count': Gauge('smb2_syscall_lchown_count', 'Number of lchown system calls'),
    'syscall_lchown_time': Gauge('smb2_syscall_lchown_time', 'Time spent in lchown system calls'),
    'syscall_chdir_count': Gauge('smb2_syscall_chdir_count', 'Number of chdir system calls'),
    'syscall_chdir_time': Gauge('smb2_syscall_chdir_time', 'Time spent in chdir system calls'),
    'syscall_getwd_count': Gauge('smb2_syscall_getwd_count', 'Number of getwd system calls'),
    'syscall_getwd_time': Gauge('smb2_syscall_getwd_time', 'Time spent in getwd system calls'),
    'syscall_ntimes_count': Gauge('smb2_syscall_ntimes_count', 'Number of ntimes system calls'),
    'syscall_ntimes_time': Gauge('smb2_syscall_ntimes_time', 'Time spent in ntimes system calls'),
    'syscall_ftruncate_count': Gauge('smb2_syscall_ftruncate_count', \
        'Number of ftruncate system calls'),
    'syscall_ftruncate_time': Gauge('smb2_syscall_ftruncate_time', \
        'Time spent in ftruncate system calls'),
    'syscall_fallocate_count': Gauge('smb2_syscall_fallocate_count', \
        'Number of fallocate system calls'),
    'syscall_fallocate_time': Gauge('smb2_syscall_fallocate_time', \
        'Time spent in fallocate system calls'),
    'syscall_fcntl_lock_count': Gauge('smb2_syscall_fcntl_lock_count', \
        'Number of fcntl lock system calls'),
    'syscall_fcntl_lock_time': Gauge('smb2_syscall_fcntl_lock_time', \
        'Time spent in fcntl lock system calls'),
    'syscall_kernel_flock_count': Gauge('smb2_syscall_kernel_flock_count', \
        'Number of kernel flock system calls'),
    'syscall_kernel_flock_time': Gauge('smb2_syscall_kernel_flock_time', \
        'Time spent in kernel flock system calls'),
    'syscall_linux_setlease_count': Gauge('smb2_syscall_linux_setlease_count', \
        'Number of Linux setlease system calls'),
    'syscall_linux_setlease_time': Gauge('smb2_syscall_linux_setlease_time', \
        'Time spent in Linux setlease system calls'),
    'syscall_fcntl_getlock_count': Gauge('smb2_syscall_fcntl_getlock_count', \
        'Number of fcntl getlock system calls'),
    'syscall_fcntl_getlock_time': Gauge('smb2_syscall_fcntl_getlock_time', \
        'Time spent in fcntl getlock system calls'),
    'syscall_readlink_count': Gauge('smb2_syscall_readlink_count', \
        'Number of readlink system calls'),
    'syscall_readlink_time': Gauge('smb2_syscall_readlink_time', \
        'Time spent in readlink system calls'),
    'syscall_symlink_count': Gauge('smb2_syscall_symlink_count', \
        'Number of symlink system calls'),
    'syscall_symlink_time': Gauge('smb2_syscall_symlink_time', \
        'Time spent in symlink system calls'),
    'syscall_link_count': Gauge('smb2_syscall_link_count', \
        'Number of link system calls'),
    'syscall_link_time': Gauge('smb2_syscall_link_time', 'Time spent in link system calls'),
    'syscall_mknod_count': Gauge('smb2_syscall_mknod_count', 'Number of mknod system calls'),
    'syscall_mknod_time': Gauge('smb2_syscall_mknod_time', 'Time spent in mknod system calls'),
    'syscall_realpath_count': Gauge('smb2_syscall_realpath_count', \
        'Number of realpath system calls'),
    'syscall_realpath_time': Gauge('smb2_syscall_realpath_time', \
        'Time spent in realpath system calls'),
    'syscall_get_quota_count': Gauge('smb2_syscall_get_quota_count', \
        'Number of get quota system calls'),
    'syscall_get_quota_time': Gauge('smb2_syscall_get_quota_time', \
        'Time spent in get quota system calls'),
    'syscall_set_quota_count': Gauge('smb2_syscall_set_quota_count', \
        'Number of set quota system calls'),
    'syscall_set_quota_time': Gauge('smb2_syscall_set_quota_time', \
        'Time spent in set quota system calls'),
    'syscall_get_sd_count': Gauge('smb2_syscall_get_sd_count', \
        'Number of get sd system calls'),
    'syscall_get_sd_time': Gauge('smb2_syscall_get_sd_time', \
        'Time spent in get sd system calls'),
    'syscall_set_sd_count': Gauge('smb2_syscall_set_sd_count', 'Number of set sd system calls'),
    'syscall_set_sd_time': Gauge('smb2_syscall_set_sd_time', 'Time spent in set sd system calls'),
    'syscall_brl_lock_count': Gauge('smb2_syscall_brl_lock_count', \
        'Number of brl lock system calls'),
    'syscall_brl_lock_time': Gauge('smb2_syscall_brl_lock_time', \
        'Time spent in brl lock system calls'),
    'syscall_brl_unlock_count': Gauge('smb2_syscall_brl_unlock_count', \
        'Number of brl unlock system calls'),
    'syscall_brl_unlock_time': Gauge('smb2_syscall_brl_unlock_time', \
        'Time spent in brl unlock system calls'),
    'syscall_brl_cancel_count': Gauge('smb2_syscall_brl_cancel_count', \
        'Number of brl cancel system calls'),
    'syscall_brl_cancel_time': Gauge('smb2_syscall_brl_cancel_time', \
        'Time spent in brl cancel system calls'),
    'get_nt_acl_count': Gauge('smb2_get_nt_acl_count', 'Number of get_nt_acl calls'),
    'get_nt_acl_time': Gauge('smb2_get_nt_acl_time', 'Time spent in get_nt_acl calls'),
    'fget_nt_acl_count': Gauge('smb2_fget_nt_acl_count', 'Number of fget_nt_acl calls'),
    'fget_nt_acl_time': Gauge('smb2_fget_nt_acl_time', 'Time spent in fget_nt_acl calls'),
    'fset_nt_acl_count': Gauge('smb2_fset_nt_acl_count', 'Number of fset_nt_acl calls'),
    'fset_nt_acl_time': Gauge('smb2_fset_nt_acl_time', 'Time spent in fset_nt_acl calls'),
    'statcache_lookups_count': Gauge('smb2_statcache_lookups_count', 'Number of statcache lookups'),
    'statcache_misses_count': Gauge('smb2_statcache_misses_count', 'Number of statcache misses'),
    'statcache_hits_count': Gauge('smb2_statcache_hits_count', 'Number of statcache hits'),
    'writecache_allocations_count': Gauge('smb2_writecache_allocations_count', \
        'Number of times memory was allocated for write cache'),
    'writecache_deallocations_count': Gauge('smb2_writecache_deallocations_count', \
        'Number of times memory was deallocated for write cache'),
    'writecache_cached_reads_count': Gauge('smb2_writecache_cached_reads_count', \
        'Number of cached reads from write cache'),
    'writecache_total_writes_count': Gauge('smb2_writecache_total_writes_count', \
        'Total number of writes to write cache'),
    'writecache_init_writes_count': Gauge('smb2_writecache_init_writes_count', \
        'Number of writes to newly allocated write cache'),
    'writecache_abutted_writes_count': Gauge('smb2_writecache_abutted_writes_count', \
        'Number of writes that abutted the end of write cache'),
    'writecache_non_oplock_writes_count': Gauge('smb2_writecache_non_oplock_writes_count', \
        'Number of non-oplock writes to write cache'),
    'writecache_direct_writes_count': Gauge('smb2_writecache_direct_writes_count', \
        'Number of direct writes to write cache'),
    'writecache_cached_writes_count': Gauge('smb2_writecache_cached_writes_count', \
        'Number of cached writes to write cache'),
    'writecache_perfect_writes_count': Gauge('smb2_writecache_perfect_writes_count', \
        'Number of writes to write cache that matched cache size'),
    'writecache_flush_reason_seek_count': Gauge('smb2_writecache_flush_reason_seek_count', \
        'Number of write cache flushes due to seek operation'),
    'writecache_flush_reason_read_count': Gauge('smb2_writecache_flush_reason_read_count', \
        'Number of write cache flushes due to read operation'),
    'writecache_flush_reason_readraw_count': Gauge('smb2_writecache_flush_reason_readraw_count', \
        'Number of write cache flushes due to read raw operation'),
    'writecache_flush_reason_write_count': Gauge('smb2_writecache_flush_reason_write_count', \
        'Number of write cache flushes due to write operation'),
    'writecache_flush_reason_oplock_count': Gauge('smb2_writecache_flush_reason_oplock_count', \
        'Number of write cache flushes due to oplock break'),
    'writecache_flush_reason_close_count': Gauge('smb2_writecache_flush_reason_close_count', \
        'Number of write cache flushes due to file close'),
    'writecache_flush_reason_sync_count': Gauge('smb2_writecache_flush_reason_sync_count', \
        'Number of write cache flushes due to sync operation'),
    'writecache_flush_reason_sizechange_count': \
        Gauge('smb2_writecache_flush_reason_sizechange_count', \
            'Number of write cache flushes due to file size change'),
    'SMBmkdir_time': Gauge('smb2_SMBmkdir_time', 'Time spent in mkdir SMB calls'),
    'SMBrmdir_count': Gauge('smb2_SMBrmdir_count', 'Number of rmdir SMB calls'),
    'SMBrmdir_time': Gauge('smb2_SMBrmdir_time', 'Time spent in rmdir SMB calls'),
    'SMBopen_count': Gauge('smb2_SMBopen_count', 'Number of open SMB calls'),
    'SMBopen_time': Gauge('smb2_SMBopen_time', 'Time spent in open SMB calls'),
    'SMBcreate_count': Gauge('smb2_SMBcreate_count', 'Number of create SMB calls'),
    'SMBcreate_time': Gauge('smb2_SMBcreate_time', 'Time spent in create SMB calls'),
    'SMBclose_count': Gauge('smb2_SMBclose_count', 'Number of close SMB calls'),
    'SMBclose_time': Gauge('smb2_SMBclose_time', 'Time spent in close SMB calls'),
    'SMBflush_count': Gauge('smb2_SMBflush_count', 'Number of flush SMB calls'),
    'SMBflush_time': Gauge('smb2_SMBflush_time', 'Time spent in flush SMB calls'),
    'SMBunlink_count': Gauge('smb2_SMBunlink_count', 'Number of unlink SMB calls'),
    'SMBunlink_time': Gauge('smb2_SMBunlink_time', 'Time spent in unlink SMB calls'),
    'SMBmv_count': Gauge('smb2_SMBmv_count', 'Number of mv SMB calls'),
    'SMBmv_time': Gauge('smb2_SMBmv_time', 'Time spent in mv SMB calls'),
    'smbgetatr_count': Gauge('smb2_samba_smbgetatr_count', 'Number of SMBgetatr operations'),
    'smbgetatr_time': Gauge('smb2_samba_smbgetatr_time', 'Time taken for SMBgetatr operations'),
    'smbsetatr_count': Gauge('smb2_samba_smbsetatr_count', 'Number of SMBsetatr operations'),
    'smbsetatr_time': Gauge('smb2_samba_smbsetatr_time', 'Time taken for SMBsetatr operations'),
    'smbread_count': Gauge('smb2_samba_smbread_count', 'Number of SMBread operations'),
    'smbread_time': Gauge('smb2_samba_smbread_time', 'Time taken for SMBread operations'),
    'smbwrite_count': Gauge('smb2_samba_smbwrite_count', 'Number of SMBwrite operations'),
    'smbwrite_time': Gauge('smb2_samba_smbwrite_time', 'Time taken for SMBwrite operations'),
    'smblock_count': Gauge('smb2_samba_smblock_count', 'Number of SMBlock operations'),
    'smblock_time': Gauge('smb2_samba_smblock_time', 'Time taken for SMBlock operations'),
    'smbunlock_count': Gauge('smb2_samba_smbunlock_count', 'Number of SMBunlock operations'),
    'smbunlock_time': Gauge('smb2_samba_smbunlock_time', 'Time taken for SMBunlock operations'),
    'smbctemp_count': Gauge('smb2_samba_smbctemp_count', 'Number of SMBctemp operations'),
    'smbctemp_time': Gauge('smb2_samba_smbctemp_time', 'Time taken for SMBctemp operations'),
    'smbmknew_count': Gauge('smb2_samba_smbmknew_count', 'Number of SMBmknew operations'),
    'smbmknew_time': Gauge('smb2_samba_smbmknew_time', 'Time taken for SMBmknew operations'),
    'smbcheckpath_count': Gauge('smb2_samba_smbcheckpath_count', \
        'Number of SMBcheckpath operations'),
    'smbcheckpath_time': Gauge('smb2_samba_smbcheckpath_time', \
        'Time taken for SMBcheckpath operations'),
    'smbexit_count': Gauge('smb2_samba_smbexit_count', 'Number of SMBexit operations'),
    'smbexit_time': Gauge('smb2_samba_smbexit_time', 'Time taken for SMBexit operations'),
    'SMBgetatr_count': Gauge('smb2_SMBgetatr_count', 'Number of SMBgetatr calls'),
    'SMBgetatr_time': Gauge('smb2SMBgetatr_time', 'Total time spent in SMBgetatr calls'),
    'SMBsetatr_count': Gauge('smb2SMBsetatr_count', 'Number of SMBsetatr calls'),
    'SMBsetatr_time': Gauge('smb2SMBsetatr_time', 'Total time spent in SMBsetatr calls'),
    'SMBread_count': Gauge('smb2SMBread_count', 'Number of SMBread calls'),
    'SMBread_time': Gauge('smb2SMBread_time', 'Total time spent in SMBread calls'),
    'SMBwrite_count': Gauge('smb2SMBwrite_count', 'Number of SMBwrite calls'),
    'SMBwrite_time': Gauge('smb2SMBwrite_time', 'Total time spent in SMBwrite calls'),
    'SMBlock_count': Gauge('smb2SMBlock_count', 'Number of SMBlock calls'),
    'SMBlock_time': Gauge('smb2SMBlock_time', 'Total time spent in SMBlock calls'),
    'SMBunlock_count': Gauge('smb2SMBunlock_count', 'Number of SMBunlock calls'),
    'SMBunlock_time': Gauge('smb2SMBunlock_time', 'Total time spent in SMBunlock calls'),
    'SMBctemp_count': Gauge('smb2SMBctemp_count', 'Number of SMBctemp calls'),
    'SMBctemp_time': Gauge('smb2SMBctemp_time', 'Total time spent in SMBctemp calls'),
    'SMBmknew_count': Gauge('smb2SMBmknew_count', 'Number of SMBmknew calls'),
    'SMBmknew_time': Gauge('smb2SMBmknew_time', 'Total time spent in SMBmknew calls'),
    'SMBcheckpath_count': Gauge('smb2SMBcheckpath_count', 'Number of SMBcheckpath calls'),
    'SMBcheckpath_time': Gauge('smb2SMBcheckpath_time', 'Total time spent in SMBcheckpath calls'),
    'SMBexit_count': Gauge('smb2SMBexit_count', 'Number of SMBexit calls'),
    'SMBexit_time': Gauge('smb2SMBexit_time', 'Total time spent in SMBexit calls'),
    'SMBlseek_count': Gauge('smb2SMBlseek_count', 'Number of SMBlseek calls'),
    'SMBlseek_time': Gauge('smb2SMBlseek_time', 'Total time spent in SMBlseek calls'),
    'SMBlockread_count': Gauge('smb2SMBlockread_count', 'Number of SMBlockread calls'),
    'SMBlockread_time': Gauge('smb2SMBlockread_time', 'Total time spent in SMBlockread calls'),
    'SMBwriteunlock_count': Gauge('smb2SMBwriteunlock_count', 'Number of SMBwriteunlock calls'),
    'SMBwriteunlock_time': Gauge('smb2SMBwriteunlock_time', \
        'Total time spent in SMBwriteunlock calls'),
    'SMBreadbraw_count': Gauge('smb2SMBreadbraw_count', 'Number of SMBreadbraw calls'),
    'SMBreadbraw_time': Gauge('smb2SMBreadbraw_time', 'Total time spent in SMBreadbraw calls'),
    'SMBreadBmpx_count': Gauge('smb2SMBreadBmpx_count', 'Number of SMBreadBmpx calls'),
    'SMBreadBmpx_time': Gauge('smb2SMBreadBmpx_time', 'Total time spent in SMBreadBmpx calls'),
    'SMBreadBs_count': Gauge('smb2SMBreadBs_count', 'Number of SMBreadBs calls'),
    'SMBreadBs_time': Gauge('smb2SMBreadBs_time', 'Total time spent in SMBreadBs calls'),
    'SMBwritebraw_count': Gauge('smb2SMBwritebraw_count', 'Number of SMBwritebraw calls'),
    'SMBwritebraw_time': Gauge('smb2_SMBwritebraw_time', \
        'The amount of time spent in SMBwritebraw (in seconds)'),
    'SMBwriteBmpx_count': Gauge('smb2_SMBwriteBmpx_count', 'The number of SMBwriteBmpx calls'),
    'SMBwriteBmpx_time': Gauge('smb2_SMBwriteBmpx_time', \
        'The amount of time spent in SMBwriteBmpx (in seconds)'),
    'SMBwriteBs_count': Gauge('smb2_SMBwriteBs_count', 'The number of SMBwriteBs calls'),
    'SMBwriteBs_time': Gauge('smb2_SMBwriteBs_time', \
        'The amount of time spent in SMBwriteBs (in seconds)'),
    'SMBwritec_count': Gauge('smb2_SMBwritec_count', 'The number of SMBwritec calls'),
    'SMBwritec_time': Gauge('smb2_SMBwritec_time', \
        'The amount of time spent in SMBwritec (in seconds)'),
    'SMBsetattrE_count': Gauge('smb2_SMBsetattrE_count', 'The number of SMBsetattrE calls'),
    'SMBsetattrE_time': Gauge('smb2_SMBsetattrE_time', \
        'The amount of time spent in SMBsetattrE (in seconds)'),
    'SMBgetattrE_count': Gauge('smb2_SMBgetattrE_count', 'The number of SMBgetattrE calls'),
    'SMBgetattrE_time': Gauge('smb2_SMBgetattrE_time', \
        'The amount of time spent in SMBgetattrE (in seconds)'),
    'SMBlockingX_count': Gauge('smb2_SMBlockingX_count', 'The number of SMBlockingX calls'),
    'SMBlockingX_time': Gauge('smb2_SMBlockingX_time', \
        'The amount of time spent in SMBlockingX (in seconds)'),
    'SMBtrans_count': Gauge('smb2_SMBtrans_count', 'The number of SMBtrans calls'),
    'SMBtrans_time': Gauge('smb2_SMBtrans_time', \
        'The amount of time spent in SMBtrans (in seconds)'),
    'SMBtranss_count': Gauge('smb2_SMBtranss_count', 'SMBtranss count'),
    'SMBtranss_time': Gauge('smb2_SMBtranss_time', 'SMBtranss time'),
    'SMBioctl_count': Gauge('smb2_SMBioctl_count', 'SMBioctl count'),
    'SMBioctl_time': Gauge('smb2_SMBioctl_time', 'SMBioctl time'),
    'SMBioctls_count': Gauge('smb2_SMBioctls_count', 'SMBioctls count'),
    'SMBioctls_time': Gauge('smb2_SMBioctls_time', 'SMBioctls time'),
    'SMBcopy_count': Gauge('smb2_SMBcopy_count', 'SMBcopy count'),
    'SMBcopy_time': Gauge('smb2_SMBcopy_time', 'SMBcopy time'),
    'SMBmove_count': Gauge('smb2_SMBmove_count', 'SMBmove count'),
    'SMBmove_time': Gauge('smb2_SMBmove_time', 'SMBmove time'),
    'SMBecho_count': Gauge('smb2_SMBecho_count', 'SMBecho count'),
    'SMBecho_time': Gauge('smb2_SMBecho_time', 'SMBecho time'),
    'SMBwriteclose_count': Gauge('smb2_SMBwriteclose_count', 'SMBwriteclose count'),
    'SMBwriteclose_time': Gauge('smb2_SMBwriteclose_time', 'SMBwriteclose time'),
    'SMBopenX_count': Gauge('smb2_SMBopenX_count', 'SMBopenX count'),
    'SMBopenX_time': Gauge('smb2_SMBopenX_time', 'SMBopenX time'),
    'SMBreadX_count': Gauge('smb2_SMBreadX_count', 'SMBreadX count'),
    'SMBreadX_time': Gauge('smb2_SMBreadX_time', 'SMBreadX time'),
    'SMBwriteX_count': Gauge('smb2_SMBwriteX_count', 'SMBwriteX count'),
    'SMBwriteX_time': Gauge('smb2_SMBwriteX_time', 'SMBwriteX time'),
    'SMBtrans2_count': Gauge('smb2_SMBtrans2_count', 'SMBtrans2 count'),
    'SMBtrans2_time': Gauge('smb2_SMBtrans2_time', 'SMBtrans2 time'),
    'SMBtranss2_count': Gauge('smb2_SMBtranss2_count', 'SMBtranss2 count'),
    'SMBtranss2_time': Gauge('smb2_SMBtranss2_time', 'SMBtranss2 time'),
    'SMBfindclose_count': Gauge('smb2_SMBfindclose_count', 'SMBfindclose count'),
    'SMBfindclose_time': Gauge('smb2_SMBfindclose_time', 'SMBfindclose time'),
    'SMBfindnclose_count': Gauge('smb2_SMBfindnclose_count', 'SMBfindnclose count'),
    'SMBfindnclose_time': Gauge('smb2_SMBfindnclose_time', 'SMBfindnclose time'),
    'SMBtcon_count': Gauge('smb2_SMBtcon_count', 'SMBtcon count'),
    'SMBtcon_time': Gauge('smb2_SMBtcon_time', 'SMBtcon time'),
    'SMBtdis_count': Gauge('smb2_SMBtdis_count', 'Number of SMBtdis requests'),
    'SMBtdis_time': Gauge('smb2_SMBtdis_time', 'Time spent on SMBtdis requests'),
    'SMBnegprot_count': Gauge('smb2_SMBnegprot_count', 'Number of SMBnegprot requests'),
    'SMBnegprot_time': Gauge('smb2_SMBnegprot_time', 'Time spent on SMBnegprot requests'),
    'SMBsesssetupx_count': Gauge('smb2_SMBsesssetupx_count', 'Number of SMBsesssetupX requests'),
    'SMBsesssetupx_time': Gauge('smb2_SMBsesssetupx_time', 'Time spent on SMBsesssetupX requests'),
    'SMBulogoffx_count': Gauge('smb2_SMBulogoffx_count', 'Number of SMBulogoffX requests'),
    'SMBulogoffx_time': Gauge('smb2_SMBulogoffx_time', 'Time spent on SMBulogoffX requests'),
    'SMBtconx_count': Gauge('smb2_SMBtconx_count', 'Number of SMBtconX requests'),
    'SMBtconx_time': Gauge('smb2_SMBtconx_time', 'Time spent on SMBtconX requests'),
    'SMBdskattr_count': Gauge('smb2_SMBdskattr_count', 'Number of SMBdskattr requests'),
    'SMBdskattr_time': Gauge('smb2_SMBdskattr_time', 'Time spent on SMBdskattr requests'),
    'SMBsearch_count': Gauge('smb2_SMBsearch_count', 'Number of SMBsearch requests'),
    'SMBsearch_time': Gauge('smb2_SMBsearch_time', 'Time spent on SMBsearch requests'),
    'SMBffirst_count': Gauge('smb2_SMBffirst_count', 'Number of SMBffirst requests'),
    'SMBffirst_time': Gauge('smb2_SMBffirst_time', 'Time spent on SMBffirst requests'),
    'SMBfunique_count': Gauge('smb2_SMBfunique_count', 'Number of SMBfunique requests'),
    'SMBfunique_time': Gauge('smb2_SMBfunique_time', 'Time spent on SMBfunique requests'),
    'SMBfclose_count': Gauge('smb2_SMBfclose_count', 'Number of SMBfclose requests'),
    'SMBfclose_time': Gauge('smb2_SMBfclose_time', 'Time spent on SMBfclose requests'),
    'SMBnttrans_count': Gauge('smb2_SMBnttrans_count', 'Number of SMBnttrans requests'),
    'SMBnttrans_time': Gauge('smb2_SMBnttrans_time', 'Time spent on SMBnttrans requests'),
    'SMBnttranss_count': Gauge('smb2_SMBnttranss_count', 'Number of SMBnttranss requests'),
    'SMBnttranss_time': Gauge('smb2_SMBnttranss_time', 'Time spent on SMBnttranss requests'),
    'SMBntcreatex_count': Gauge('smb2_SMBntcreatex_count', 'Number of SMBntcreateX requests'),
    'SMBntcreatex_time': Gauge('smb2_SMBntcreatex_time', 'Time spent on SMBntcreateX requests'),
    'SMBntcancel_count': Gauge('smb2_SMBntcancel_count', 'Number of SMBntcancel requests'),
    'SMBntcancel_time': Gauge('smb2_SMBntcancel_time', 'Time spent on SMBntcancel requests'),
    'SMBntrename_count': Gauge('smb2_SMBntrename_count', 'Number of SMBntrename requests'),
    'SMBntrename_time': Gauge('smb2_SMBntrename_time', 'SMBntrename time'),
    'SMBsplopen_count': Gauge('smb2_SMBsplopen_count', 'SMBsplopen count'),
    'SMBsplopen_time': Gauge('smb2_SMBsplopen_time', 'SMBsplopen time'),
    'SMBsplwr_count': Gauge('smb2_SMBsplwr_count', 'SMBsplwr count'),
    'SMBsplwr_time': Gauge('smb2_SMBsplwr_time', 'SMBsplwr time'),
    'SMBsplclose_count': Gauge('smb2_SMBsplclose_count', 'SMBsplclose count'),
    'SMBsplclose_time': Gauge('smb2_SMBsplclose_time', 'SMBsplclose time'),
    'SMBsplretq_count': Gauge('smb2_SMBsplretq_count', 'SMBsplretq count'),
    'SMBsplretq_time': Gauge('smb2_SMBsplretq_time', 'SMBsplretq time'),
    'SMBsends_count': Gauge('smb2_SMBsends_count', 'SMBsends count'),
    'SMBsends_time': Gauge('smb2_SMBsends_time', 'SMBsends time'),
    'SMBsendb_count': Gauge('smb2_SMBsendb_count', 'SMBsendb count'),
    'SMBsendb_time': Gauge('smb2_SMBsendb_time', 'SMBsendb time'),
    'SMBfwdname_count': Gauge('smb2_SMBfwdname_count', 'SMBfwdname count'),
    'SMBfwdname_time': Gauge('smb2_SMBfwdname_time', 'SMBfwdname time'),
    'SMBcancelf_count': Gauge('smb2_SMBcancelf_count', 'SMBcancelf count'),
    'SMBcancelf_time': Gauge('smb2_SMBcancelf_time', 'SMBcancelf time'),
    'SMBgetmac_count': Gauge('smb2_SMBgetmac_count', 'SMBgetmac count'),
    'SMBgetmac_time': Gauge('smb2_SMBgetmac_time', 'SMBgetmac time'),
    'SMBsendstrt_count': Gauge('smb2_SMBsendstrt_count', 'SMBsendstrt count'),
    'SMBsendstrt_time': Gauge('smb2_SMBsendstrt_time', 'SMBsendstrt time'),
    'SMBsendend_count': Gauge('smb2_SMBsendend_count', 'SMBsendend count'),
    'SMBsendend_time': Gauge('smb2_SMBsendend_time', 'SMBsendend time'),
    'SMBsendtxt_count': Gauge('smb2_SMBsendtxt_count', 'SMBsendtxt count'),
    'SMBsendtxt_time': Gauge('smb2_SMBsendtxt_time', 'SMBsendtxt time'),
    'SMBinvalid_count': Gauge('smb2_SMBinvalid_count', 'SMBinvalid count'),
    'SMBinvalid_time': Gauge('smb2_SMBinvalid_time', 'SMBinvalid time'),
    'trans2_open_count': Gauge('smb2_Trans2_open_count', 'Trans2 open count'),
    'trans2_open_time': Gauge('smb2_Trans2_open_time', 'Trans2 open time'),
    'trans2_findfirst_count': Gauge('smb2_Trans2_findfirst_count', 'Trans2 findfirst count'),
    'trans2_findfirst_time': Gauge('smb2_Trans2_findfirst_time', 'Trans2 findfirst time'),
    'trans2_findnext_count': Gauge('smb2_Trans2_findnext_count', 'Trans2 findnext count'),
    'trans2_findnext_time': Gauge('smb2_Trans2_findnext_time', 'Trans2 findnext time'),
    'trans2_qfsinfo_count': Gauge('smb2_Trans2_qfsinfo_count', 'Trans2 qfsinfo count'),
    'trans2_qfsinfo_time': Gauge('smb2_Trans2_qfsinfo_time', 'Trans2 qfsinfo time'),
    'trans2_setfsinfo_count': Gauge('smb2_Trans2_setfsinfo_count', 'Trans2 setfsinfo count'),
    'trans2_setfsinfo_time': Gauge('smb2_Trans2_setfsinfo_time', 'Trans2 setfsinfo time'),
    'trans2_qpathinfo_count': Gauge('smb2_Trans2_qpathinfo_count', 'Trans2 qpathinfo count'),
    'trans2_qpathinfo_time': Gauge('smb2_Trans2_qpathinfo_time', 'Trans2 qpathinfo time'),
    'trans2_setpathinfo_count': Gauge('smb2_Trans2_setpathinfo_count', 'Trans2 setpathinfo count'),
    'trans2_setpathinfo_time': Gauge('smb2_Trans2_setpathinfo_time', 'Trans2 setpathinfo time'),
    'trans2_qfileinfo_count': Gauge('smb2_Trans2_qfileinfo_count', 'Trans2 qfileinfo count'),
    'trans2_qfileinfo_time': Gauge('smb2_Trans2_qfileinfo_time', 'Trans2 qfileinfo time'),
    'Trans2_setfileinfo_count': Gauge('smb2_Trans2_setfileinfo_count', 'Trans2_setfileinfo count'),
    'Trans2_setfileinfo_time': Gauge('smb2_Trans2_setfileinfo_time', 'Trans2_setfileinfo time'),
    'Trans2_fsctl_count': Gauge('smb2_Trans2_fsctl_count', 'Trans2_fsctl count'),
    'Trans2_fsctl_time': Gauge('smb2_Trans2_fsctl_time', 'Trans2_fsctl time'),
    'Trans2_ioctl_count': Gauge('smb2_Trans2_ioctl_count', 'Trans2_ioctl count'),
    'Trans2_ioctl_time': Gauge('smb2_Trans2_ioctl_time', 'Trans2_ioctl time'),
    'Trans2_findnotifyfirst_count': \
        Gauge('smb2_Trans2_findnotifyfirst_count', 'Trans2_findnotifyfirst count'),
    'Trans2_findnotifyfirst_time': \
        Gauge('smb2_Trans2_findnotifyfirst_time', 'Trans2_findnotifyfirst time'),
    'Trans2_findnotifynext_count': \
        Gauge('smb2_Trans2_findnotifynext_count', 'Trans2_findnotifynext count'),
    'Trans2_findnotifynext_time': \
        Gauge('smb2_Trans2_findnotifynext_time', 'Trans2_findnotifynext time'),
    'Trans2_mkdir_count': \
        Gauge('smb2_Trans2_mkdir_count', 'Trans2_mkdir count'),
    'Trans2_mkdir_time': \
        Gauge('smb2_Trans2_mkdir_time', 'Trans2_mkdir time'),
    'Trans2_session_setup_count': \
        Gauge('smb2_Trans2_session_setup_count', 'Trans2_session_setup count'),
    'Trans2_session_setup_time': \
        Gauge('smb2_Trans2_session_setup_time', 'Trans2_session_setup time'),
    'Trans2_get_dfs_referral_count': \
        Gauge('smb2_Trans2_get_dfs_referral_count', 'Trans2_get_dfs_referral count'),
    'Trans2_get_dfs_referral_time': \
        Gauge('smb2_Trans2_get_dfs_referral_time', 'Trans2_get_dfs_referral time'),
    'Trans2_report_dfs_inconsistancy_count': \
        Gauge('smb2_Trans2_report_dfs_inconsistancy_count', \
            'Trans2_report_dfs_inconsistancy count'),
    'Trans2_report_dfs_inconsistancy_time': \
        Gauge('smb2_Trans2_report_dfs_inconsistancy_time', \
            'Trans2_report_dfs_inconsistancy time'),
    'NT_transact_create_count': \
        Gauge('NT_transact_create_count', 'NT transact create count'),
    'NT_transact_create_time': \
        Gauge('NT_transact_create_time', 'NT transact create time'),
    'NT_transact_ioctl_count': \
        Gauge('NT_transact_ioctl_count', 'NT transact ioctl count'),
    'NT_transact_ioctl_time': \
        Gauge('NT_transact_ioctl_time', 'NT transact ioctl time'),
    'NT_transact_set_security_desc_count': \
        Gauge('NT_transact_set_security_desc_count', 'NT transact set security desc count'),
    'NT_transact_set_security_desc_time': \
        Gauge('NT_transact_set_security_desc_time', 'NT transact set security desc time'),
    'NT_transact_notify_change_count': \
        Gauge('NT_transact_notify_change_count', 'NT transact notify change count'),
    'NT_transact_notify_change_time': \
        Gauge('NT_transact_notify_change_time', 'NT transact notify change time'),
    'NT_transact_rename_count': \
        Gauge('NT_transact_rename_count', 'NT transact rename count'),
    'NT_transact_rename_time': \
        Gauge('NT_transact_rename_time', 'NT transact rename time'),
    'NT_transact_query_security_desc_count': \
        Gauge('NT_transact_query_security_desc_count', \
            'NT transact query security desc count'),
    'NT_transact_query_security_desc_time': \
        Gauge('NT_transact_query_security_desc_time', \
            'NT transact query security desc time'),
    'NT_transact_get_user_quota_count': \
        Gauge('NT_transact_get_user_quota_count', 'NT transact get user quota count'),
    'NT_transact_get_user_quota_time': \
        Gauge('NT_transact_get_user_quota_time', 'NT transact get user quota time'),
    'NT_transact_set_user_quota_count': \
        Gauge('NT_transact_set_user_quota_count', 'NT transact set user quota count'),
    'NT_transact_set_user_quota_time': \
        Gauge('NT_transact_set_user_quota_time', 'NT transact set user quota time'),
    'smb2_negprot_count': Gauge('smb2_negprot_count', \
        'Number of SMB2 negotiation protocol requests'),
    'smb2_negprot_time': Gauge('smb2_negprot_time', \
        'Total time spent on SMB2 negotiation protocol requests'),
    'smb2_negprot_idle': Gauge('smb2_negprot_idle', \
        'Total idle time during SMB2 negotiation protocol requests'),
    'smb2_negprot_inbytes': Gauge('smb2_negprot_inbytes', \
        'Total input bytes received during SMB2 negotiation protocol requests'),
    'smb2_negprot_outbytes': Gauge('smb2_negprot_outbytes', \
        'Total output bytes sent during SMB2 negotiation protocol requests'),
    'smb2_sesssetup_count': Gauge('smb2_sesssetup_count', \
        'Number of SMB2 session setup requests'),
    'smb2_sesssetup_time': Gauge('smb2_sesssetup_time', \
        'Total time spent on SMB2 session setup requests'),
    'smb2_sesssetup_idle': Gauge('smb2_sesssetup_idle', \
        'Total idle time during SMB2 session setup requests'),
    'smb2_sesssetup_inbytes': Gauge('smb2_sesssetup_inbytes', \
        'Total input bytes received during SMB2 session setup requests'),
    'smb2_sesssetup_outbytes': Gauge('smb2_sesssetup_outbytes', \
        'Total output bytes sent during SMB2 session setup requests'),
    'smb2_logoff_count': Gauge('smb2_logoff_count', \
        'Number of SMB2 logoff requests'),
    'smb2_logoff_time': Gauge('smb2_logoff_time', \
        'Total time spent on SMB2 logoff requests'),
    'smb2_logoff_idle': Gauge('smb2_logoff_idle', \
        'Total idle time during SMB2 logoff requests'),
    'smb2_logoff_inbytes': Gauge('smb2_logoff_inbytes', \
        'Total input bytes received during SMB2 logoff requests'),
    'smb2_logoff_outbytes': Gauge('smb2_logoff_outbytes', \
        'Total output bytes sent during SMB2 logoff requests'),
    'smb2_tcon_count': Gauge('smb2_tcon_count', \
        'Number of SMB2 tree connect requests'),
    'smb2_tcon_time': Gauge('smb2_tcon_time', \
        'Total time spent on SMB2 tree connect requests'),
    'smb2_tcon_idle': Gauge('smb2_tcon_idle', \
        'Total idle time during SMB2 tree connect requests'),
    'smb2_tcon_inbytes': Gauge('smb2_tcon_inbytes', \
        'Total input bytes received during SMB2 tree connect requests'),
    'smb2_tcon_outbytes': Gauge('smb2_tcon_outbytes', \
        'Total output bytes sent during SMB2 tree connect requests'),
    'smb2_tdis_count': Gauge('smb2_tdis_count', \
        'Number of SMB2 tree disconnect requests'),
    'smb2_tdis_time': Gauge('smb2_tdis_time', 'SMB2 TDIS Time'),
    'smb2_tdis_idle': Gauge('smb2_tdis_idle', 'SMB2 TDIS Idle'),
    'smb2_tdis_inbytes': Gauge('smb2_tdis_inbytes', 'SMB2 TDIS Inbytes'),
    'smb2_tdis_outbytes': Gauge('smb2_tdis_outbytes', 'SMB2 TDIS Outbytes'),
    'smb2_create_count': Gauge('smb2_create_count', 'SMB2 Create Count'),
    'smb2_create_time': Gauge('smb2_create_time', 'SMB2 Create Time'),
    'smb2_create_idle': Gauge('smb2_create_idle', 'SMB2 Create Idle'),
    'smb2_create_inbytes': Gauge('smb2_create_inbytes', 'SMB2 Create Inbytes'),
    'smb2_create_outbytes': Gauge('smb2_create_outbytes', 'SMB2 Create Outbytes'),
    'smb2_close_count': Gauge('smb2_close_count', 'SMB2 Close Count'),
    'smb2_close_time': Gauge('smb2_close_time', 'SMB2 Close Time'),
    'smb2_close_idle': Gauge('smb2_close_idle', 'SMB2 Close Idle'),
    'smb2_close_inbytes': Gauge('smb2_close_inbytes', 'SMB2 Close Inbytes'),
    'smb2_close_outbytes': Gauge('smb2_close_outbytes', 'SMB2 Close Outbytes'),
    'smb2_flush_count': Gauge('smb2_flush_count', 'SMB2 Flush Count'),
    'smb2_flush_time': Gauge('smb2_flush_time', 'SMB2 Flush Time'),
    'smb2_flush_idle': Gauge('smb2_flush_idle', 'SMB2 Flush Idle'),
    'smb2_flush_inbytes': Gauge('smb2_flush_inbytes', 'SMB2 Flush Inbytes'),
    'smb2_flush_outbytes': Gauge('smb2_flush_outbytes', 'SMB2 Flush Outbytes'),
    'smb2_read_count': Gauge('smb2_read_count', 'SMB2 Read Count'),
    'smb2_read_time': Gauge('smb2_read_time', 'SMB2 Read Time'),
    'smb2_read_idle': Gauge('smb2_read_idle', 'SMB2 Read Idle'),
    'smb2_read_inbytes': Gauge('smb2_read_inbytes', 'SMB2 Read Inbytes'),
    'smb2_read_outbytes': Gauge('smb2_read_outbytes', 'SMB2 Read Outbytes'),
    'smb2_write_count': Gauge('smb2_write_count', 'SMB2 Write Count'),
    'smb2_write_time': Gauge('smb2_write_time', 'SMB2 Write Time'),
    'smb2_write_idle': Gauge('smb2_write_idle', 'SMB2 Write Idle'),
    'smb2_write_inbytes': Gauge('smb2_write_inbytes', 'SMB2 Write Inbytes'),
    'smb2_write_outbytes': Gauge('smb2_write_outbytes', 'SMB2 Write Outbytes'),
    'smb2_lock_count': Gauge('smb2_lock_count', 'SMB2 Lock Count'),
    'smb2_lock_time': Gauge('smb2_lock_time', 'SMB2 Lock Time'),
    'smb2_lock_idle': Gauge('smb2_lock_idle', 'SMB2 Lock Idle'),
    'smb2_lock_inbytes': Gauge('smb2_lock_inbytes', 'SMB2 Lock Inbytes'),
    'smb2_lock_outbytes': Gauge('smb2_lock_outbytes', 'SMB2 Lock Outbytes'),
    'smb2_ioctl_count': Gauge('smb2_ioctl_count', 'SMB2 Ioctl Count'),
    'smb2_ioctl_time': Gauge('smb2_ioctl_time', 'SMB2 Ioctl Time'),
    'smb2_ioctl_idle': Gauge('smb2_ioctl_idle', 'SMB2 Ioctl Idle'),
    'smb2_ioctl_inbytes': Gauge('smb2_ioctl_inbytes', 'SMB2 Ioctl Inbytes'),
    'smb2_ioctl_outbytes': Gauge('smb2_ioctl_outbytes', 'SMB2 Ioctl Outbytes'),
    'smb2_cancel_count': Gauge('smb2_cancel_count', 'SMB2 Cancel Count'),
    'smb2_cancel_time': Gauge('smb2_cancel_time', 'SMB2 Cancel Time'),
    'smb2_cancel_idle': Gauge('smb2_cancel_idle', 'SMB2 Cancel Idle'),
    'smb2_cancel_inbytes': Gauge('smb2_cancel_inbytes', 'SMB2 Cancel Inbytes'),
    'smb2_cancel_outbytes': Gauge('smb2_cancel_outbytes', 'SMB2 Cancel Outbytes'),
    'smb2_keepalive_count': Gauge('smb2_keepalive_count', 'SMB2 Keepalive Count'),
    'smb2_keepalive_time': Gauge('smb2_keepalive_time', 'SMB2 Keepalive Time'),
    'smb2_keepalive_idle': Gauge('smb2_keepalive_idle', 'SMB2 Keepalive Idle'),
    'smb2_keepalive_inbytes': Gauge('smb2_keepalive_inbytes', 'SMB2 Keepalive Inbytes'),
    'smb2_keepalive_outbytes': Gauge('smb2_keepalive_outbytes', 'SMB2 Keepalive Outbytes'),
    'smb2_find_count': Gauge('smb2_find_count', 'SMB2 Find Count'),
    'smb2_find_time': Gauge('smb2_find_time', 'SMB2 Find Time'),
    'smb2_find_idle': Gauge('smb2_find_idle', 'SMB2 Find Idle'),
    'smb2_find_inbytes': Gauge('smb2_find_inbytes', 'SMB2 Find Inbytes'),
    'smb2_find_outbytes': Gauge('smb2_find_outbytes', 'SMB2 Find Outbytes'),
    'smb2_notify_count': Gauge('smb2_notify_count', 'SMB2 Notify Count'),
    'smb2_notify_time': Gauge('smb2_notify_time', 'SMB2 Notify Time'),
    'smb2_notify_idle': Gauge('smb2_notify_idle', 'SMB2 Notify Idle'),
    'smb2_notify_inbytes': Gauge('smb2_notify_inbytes', 'SMB2 Notify Inbytes'),
    'smb2_notify_outbytes': Gauge('smb2_notify_outbytes', 'SMB2 Notify Outbytes'),
    'smb2_getinfo_count': Gauge('smb2_getinfo_count', 'SMB2 Getinfo Count'),
    'smb2_getinfo_time': Gauge('smb2_getinfo_time', 'SMB2 Getinfo Time'),
    'smb2_getinfo_idle': Gauge('smb2_getinfo_idle', 'SMB2 Getinfo Idle'),
    'smb2_getinfo_inbytes': Gauge('smb2_getinfo_inbytes', 'SMB2 Getinfo Inbytes'),
    'smb2_getinfo_outbytes': Gauge('smb2_getinfo_outbytes', 'SMB2 Getinfo Outbytes'),
    'smb2_setinfo_count': Gauge('smb2_setinfo_count', 'SMB2 Setinfo Count'),
    'smb2_setinfo_time': Gauge('smb2_setinfo_time', 'SMB2 Setinfo Time'),
    'smb2_setinfo_idle': Gauge('smb2_setinfo_idle', 'SMB2 Setinfo Idle'),
    'smb2_setinfo_inbytes': Gauge('smb2_setinfo_inbytes', 'SMB2 Setinfo Inbytes'),
    'smb2_setinfo_outbytes': Gauge('smb2_setinfo_outbytes', 'SMB2 Setinfo Outbytes'),
    'smb2_break_count': Gauge('smb2_break_count', 'SMB2 Break Count'),
    'smb2_break_time': Gauge('smb2_break_time', 'SMB2 Break Time'),
    'smb2_break_idle': Gauge('smb2_break_idle', 'SMB2 Break Idle'),
    'smb2_break_inbytes': Gauge('smb2_break_inbytes', 'SMB2 Break Inbytes'),
    'smb2_break_outbytes': Gauge('smb2_break_outbytes', 'SMB2 Break Outbytes'),

}


class SmbMetric(BaseModel):
    '''
    Pydantic smb metrics
    '''
    name: str
    value: float


def collect_metrics() -> List[Tuple[str, float]]:
    """
    Collects metrics by running the smbstatus command and extracting metrics from its output.
    """
    # Run /tmw-nas-3p/samba/bin/smbstatus -P command and capture output
    try:
        docker_output = subprocess.check_output(
            "docker ps | awk '{print $NF}' | grep cifs",
            stderr=subprocess.STDOUT,
            shell=True,
            encoding='utf-8')
    except subprocess.CalledProcessError:
        docker_output = ''

    if docker_output:
        for i in docker_output.split('\n'):
            if i:
                docker_cifs = i.split()[0]
                output = subprocess.check_output(
                    ['docker', 'exec', '-t', docker_cifs, '/tmw-nas-3p/samba/bin/smbstatus', '-P'])
                smb_metrics = extract_metrics(output.decode('utf-8'))
                for smb_metric in smb_metrics:
                    if smb_metric.name in metrics_mapping:
                        metrics_mapping[smb_metric.name].set(smb_metric.value)
    else:
        output = subprocess.check_output(
            ['/tmw-nas-3p/samba/bin/smbstatus', '-P'], encoding='utf-8')
        smb_metrics = extract_metrics(output)
        for smb_metric in smb_metrics:
            if smb_metric.name in metrics_mapping:
                metrics_mapping[smb_metric.name].set(smb_metric.value)


def extract_metrics(output: str) -> List[SmbMetric]:
    """
    Extracts metrics from smbstatus command output
    """
    smb_metrics = []
    for line in output.split('\n'):
        match = re.match(r'^([a-zA-Z0-9_]+):\s+([0-9]+)$', line.strip())
        if match:
            smb_metric = SmbMetric(
                name=match.group(1), value=float(
                    match.group(2)))
            smb_metrics.append(smb_metric)
    return smb_metrics


if __name__ == '__main__':
    """ Starts the Prometheus HTTP server and collects metrics every 5 seconds."""

    start_http_server(9090)  # Start Prometheus HTTP server

    while True:  # Collect metrics every 5 seconds
        collect_metrics()
        time.sleep(5)
