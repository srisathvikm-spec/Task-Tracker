/**
 * TaskForm component – modal form for creating/editing tasks.
 */

import React, { useEffect } from 'react';
import { Modal, Form, Input, DatePicker, Select } from 'antd';
import type { Task, TaskCreate } from '../types/task';
import type { Project } from '../types/project';
import type { User } from '../types/user';
import dayjs from 'dayjs';

interface Props {
  open: boolean;
  task?: Task | null;
  projects: Project[];
  users: User[];
  canAssign: boolean;
  onSubmit: (values: TaskCreate) => void;
  onCancel: () => void;
}

const TaskForm: React.FC<Props> = ({ open, task, projects, users, canAssign, onSubmit, onCancel }) => {
  const [form] = Form.useForm();

  useEffect(() => {
    if (open) {
      if (task) {
        form.setFieldsValue({
          title: task.title,
          description: task.description,
          due_date: task.due_date ? dayjs(task.due_date) : undefined,
          project_id: task.project_id,
          assigned_to: task.assigned_to?.id,
        });
      } else {
        form.resetFields();
      }
    }
  }, [open, task, form]);

  const handleOk = () => {
    form.validateFields().then((values) => {
      onSubmit({
        ...values,
        due_date: values.due_date ? values.due_date.format('YYYY-MM-DD') : undefined,
      });
    });
  };

  return (
    <Modal
      title={task ? 'Edit Task' : 'Create Task'}
      open={open}
      onOk={handleOk}
      onCancel={onCancel}
      destroyOnClose
    >
      <Form form={form} layout="vertical">
        <Form.Item name="title" label="Title" rules={[{ required: true, message: 'Title is required' }]}>
          <Input />
        </Form.Item>
        <Form.Item name="description" label="Description">
          <Input.TextArea rows={3} />
        </Form.Item>
        <Form.Item name="due_date" label="Due Date">
          <DatePicker style={{ width: '100%' }} />
        </Form.Item>
        <Form.Item name="project_id" label="Project" rules={[{ required: true, message: 'Project is required' }]}>
          <Select
            placeholder="Select project"
            options={projects.map((p) => ({ label: p.name, value: p.id }))}
          />
        </Form.Item>
        {canAssign && (
          <Form.Item name="assigned_to" label="Assign To">
            <Select
              placeholder="Unassigned"
              allowClear
              options={users.map((u) => ({
                label: `${u.name} (${u.email})`,
                value: u.id,
              }))}
            />
          </Form.Item>
        )}
      </Form>
    </Modal>
  );
};

export default TaskForm;
