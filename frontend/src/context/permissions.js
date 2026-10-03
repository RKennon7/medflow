/**
 * central file to track permissions allowed for User roles
 */

export const can = {
    edit: (role) => ["Clinical Admin", "Field Technician"].includes(role),
    delete: (role) => ["Clinical Admin"].includes(role),
    uploadServiceReport: (role) => ["Clinical Admin", "Field Technician"].includes(role),
    editAllFields: (role) => ["Clinical Admin"].includes(role),
};