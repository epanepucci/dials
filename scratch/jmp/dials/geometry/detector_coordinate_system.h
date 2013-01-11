
#ifndef DIALS_GEOMETRY_DETECTOR_COORDINATE_SYSTEM_H
#define DIALS_GEOMETRY_DETECTOR_COORDINATE_SYSTEM_H

#include <scitbx/vec2.h>
#include <scitbx/vec3.h>

namespace dials { namespace geometry {

/** Class representing the detector coordinate system */
class DetectorCoordinateSystem {

public:

    /** Default constructor */
    DetectorCoordinateSystem() {}

    /**
     * Initialise coordinate system by x and y axis
     * @param x_axis The x axis
     * @param y_axis The y axis
     */
    DetectorCoordinateSystem(scitbx::vec3 <double> x_axis,
                             scitbx::vec3 <double> y_axis)
        : _x_axis(x_axis),
          _y_axis(y_axis),
          _normal(x_axis.cross(y_axis).normalize()) {}

    /**
     * Initialise coordinate system by x and y axis and normal
     * @param x_axis The x axis
     * @param y_axis The y axis
     * @param normal The detector normal
     */    
    DetectorCoordinateSystem(scitbx::vec3 <double> x_axis,
                             scitbx::vec3 <double> y_axis,
                             scitbx::vec3 <double> normal)
        : _x_axis(x_axis),
          _y_axis(y_axis),
          _normal(normal) {}

public:

    /** Get the x axis vector */
    scitbx::vec3 <double> get_x_axis() {
        return _x_axis;
    }
    
    /** Get the y axis vector */
    scitbx::vec3 <double> get_y_axis() {
        return _y_axis;
    }
    
    /** Get the normal vector */
    scitbx::vec3 <double> get_normal() {
        return _normal;
    }
    
    /** Set the x axis vector */
    void set_x_axis(scitbx::vec3 <double> x_axis) {
        _x_axis = x_axis;
    }
    
    /** Set the y axis vector */
    void set_y_axis(scitbx::vec3 <double> y_axis) {
        _y_axis = y_axis;
    }
    
    /** Set the normal vector */
    void set_normal(scitbx::vec3 <double> normal) {
        _normal = normal;
    }

    /**
     * Convert the detector coordinate system to pixel units
     * @param pixel_size The size of each pixel in mm
     * @returns The coordinate system with x, y axis scaled in pixel units
     */
    DetectorCoordinateSystem in_pixel_units(scitbx::vec2 <double> pixel_size) {
        return DetectorCoordinateSystem(
            this->get_x_axis().normalize() / pixel_size[0],
            this->get_y_axis().normalize() / pixel_size[1],
            this->get_normal());
    }

    /**
     * Convert the detector coordinate system to si units
     * @param pixel_size The size of each pixel in mm
     * @returns The coordinate system with x, y axis scaled in mm
     */
    DetectorCoordinateSystem in_si_units(scitbx::vec2 <double> pixel_size) {
        return DetectorCoordinateSystem(
            this->get_x_axis().normalize() * pixel_size[0],
            this->get_y_axis().normalize() * pixel_size[1],
            this->get_normal());
    }

private:

    scitbx::vec3 <double> _x_axis;
    scitbx::vec3 <double> _y_axis;
    scitbx::vec3 <double> _normal;
};

}} // namespace = dials::geometry

#endif // DIALS_GEOMETRY_DETECTOR_COORDINATE_SYSTEM_H
