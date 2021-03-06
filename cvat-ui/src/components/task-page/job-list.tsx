import React from 'react';

import {
    Row,
    Col,
    Table,
} from 'antd';

import Text from 'antd/lib/typography/Text';
import Title from 'antd/lib/typography/Title';

import moment from 'moment';

import UserSelector from './user-selector';
import getCore from '../../core';

const core = getCore();

const baseURL = core.config.backendAPI.slice(0, -7);

interface Props {
    taskInstance: any;
    registeredUsers: any[];
    onJobUpdate(jobInstance: any): void;
}

export default function JobListComponent(props: Props) {
    const { jobs } = props.taskInstance;
    const columns = [{
        title: 'Job',
        dataIndex: 'job',
        key: 'job',
        render: (id: number) => {
            return (
                <a href={`${baseURL}/?id=${id}`}>{ `Job #${id++}` }</a>
            );
        }
    }, {
        title: 'Frames',
        dataIndex: 'frames',
        key: 'frames',
        className: 'cvat-black-color',
    }, {
        title: 'Status',
        dataIndex: 'status',
        key: 'status',
        render: (status: string) => {
            const progressColor = status === 'completed' ? 'cvat-job-completed-color':
                status === 'validation' ? 'cvat-job-validation-color' : 'cvat-job-annotation-color';

            return (
                <Text strong className={progressColor}>{ status }</Text>
            );
        }
    }, {
        title: 'Started on',
        dataIndex: 'started',
        key: 'started',
        className: 'cvat-black-color',
    }, {
        title: 'Duration',
        dataIndex: 'duration',
        key: 'duration',
        className: 'cvat-black-color',
    }, {
        title: 'Assignee',
        dataIndex: 'assignee',
        key: 'assignee',
        render: (jobInstance: any) => {
            const assignee = jobInstance.assignee ? jobInstance.assignee.username : null
            return (
                <UserSelector
                    users={props.registeredUsers}
                    value={assignee}
                    onChange={(value: string) => {
                        let [userInstance] = props.registeredUsers
                                .filter((user: any) => user.username === value);

                        if (userInstance === undefined) {
                            userInstance = null;
                        }

                        jobInstance.assignee = userInstance;
                        props.onJobUpdate(jobInstance);
                    }}
                />
            );
        },
    }];

    let completed = 0;
    const data = jobs.reduce((acc: any[], job: any) => {
        if (job.status === 'completed') {
            completed++;
        }

        const created = moment(props.taskInstance.createdDate);

        acc.push({
            key: job.id,
            job: job.id,
            frames: `${job.startFrame}-${job.stopFrame}`,
            status: `${job.status}`,
            started: `${created.format('MMMM Do YYYY HH:MM')}`,
            duration: `${moment.duration(moment(moment.now()).diff(created)).humanize()}`,
            assignee: job,
        });

        return acc;
    }, []);

    return (
        <div className='cvat-task-job-list'>
            <Row type='flex' justify='space-between' align='middle'>
                <Col>
                    <Title level={4} className='cvat-black-color cvat-jobs-header'> Jobs </Title>
                </Col>
                <Col>
                    <Text className='cvat-black-color'>
                        {`${completed} of ${data.length} jobs`}
                    </Text>
                </Col>
            </Row>
            <Table
                className='cvat-task-jobs-table'
                columns={columns}
                dataSource={data}
                size='small'
            />
        </div>
    );
}